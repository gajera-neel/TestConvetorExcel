import re
from decimal import Decimal, InvalidOperation


MONEY_RE = re.compile(r"(?:rs\.?|inr|usd|\$|₹)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\b")
ITEM_WITH_GST_RE = re.compile(
    r"^\s*(?P<serial>\d+)\s+"
    r"(?P<item>.+?)\s+"
    r"(?P<qty>\d+(?:\.\d+)?)\s+"
    r"(?:rs\.?|inr|usd|\$|₹)?\s*(?P<rate>[0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s+"
    r"(?P<gst>\d+(?:\.\d+)?)%\s+"
    r"(?:rs\.?|inr|usd|\$|₹)?\s*(?P<amount>[0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s*$",
    re.IGNORECASE,
)

ALIASES = {
    "store name": ("store", "vendor", "company", "shop", "merchant"),
    "seller": ("seller", "supplier"),
    "invoice number": ("invoice no", "invoice number", "inv no", "bill no", "receipt no"),
    "date": ("date", "bill date", "invoice date"),
    "gst number": ("gstin", "gst no", "gst number"),
    "gst amount": ("gst amount", "cgst", "sgst", "igst", "gst"),
    "phone": ("phone", "mobile", "contact"),
    "customer": ("customer", "customer name", "billed to"),
    "buyer": ("buyer", "bill to", "billed to"),
    "tax": ("tax", "vat"),
    "discount": ("discount", "disc"),
    "total": ("grand total", "net total", "total amount", "amount due", "total"),
    "payment method": ("payment method", "paid by", "mode"),
}


def _title_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip(" :-#")).title()


def _clean_amount(value: str) -> str:
    cleaned = value.replace(",", "").replace(" ", "")
    try:
        return str(Decimal(cleaned).quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        return value.strip()


def _normalize_label(label: str) -> str:
    lowered = label.lower().strip(" :-#")
    for canonical, labels in ALIASES.items():
        if any(alias == lowered or alias in lowered for alias in labels):
            return canonical.title()
    return _title_label(label)


def _extract_label_value_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}

    for line in lines:
        store_date = re.match(r"^(?P<store>.+?)\s+Date:\s*(?P<date>.+)$", line, flags=re.IGNORECASE)
        if store_date:
            fields.setdefault("Store Name", store_date.group("store").strip())
            fields.setdefault("Date", store_date.group("date").strip())
            continue

        address_gst = re.match(r"^(?P<address>.+?)\s+GSTIN:\s*(?P<gst>.+)$", line, flags=re.IGNORECASE)
        if address_gst:
            fields.setdefault("Address", address_gst.group("address").strip())
            fields.setdefault("Gst Number", address_gst.group("gst").strip())
            continue

        customer_payment = re.match(
            r"^Customer Name:\s*(?P<customer>.+?)\s+Payment Mode:\s*(?P<payment>.+)$",
            line,
            flags=re.IGNORECASE,
        )
        if customer_payment:
            fields.setdefault("Customer", customer_payment.group("customer").strip())
            fields.setdefault("Payment Method", customer_payment.group("payment").strip())
            continue

        if "mobile:" in line.lower() and "due date:" in line.lower():
            phone_part, due_part = re.split(r"\s+Due Date:\s*", line, maxsplit=1, flags=re.IGNORECASE)
            fields.setdefault("Phone", re.sub(r"^Mobile:\s*", "", phone_part, flags=re.IGNORECASE).strip())
            fields.setdefault("Due Date", due_part.strip())
            continue

        address_supply = re.match(
            r"^Address:\s*(?P<address>.+?)\s+Place of Supply:\s*(?P<supply>.+)$",
            line,
            flags=re.IGNORECASE,
        )
        if address_supply:
            fields.setdefault("Address", address_supply.group("address").strip())
            fields.setdefault("Place Of Supply", address_supply.group("supply").strip())
            continue

        if ":" in line:
            label, value = line.split(":", 1)
            if 2 <= len(label.strip()) <= 35 and value.strip():
                fields[_normalize_label(label)] = value.strip()

    for canonical, labels in ALIASES.items():
        if canonical in {"tax", "gst amount", "discount", "total"}:
            continue
        if canonical.title() in fields:
            continue
        for line in lines:
            lowered = line.lower()
            for label in labels:
                if label in lowered:
                    value = re.sub(label, "", line, flags=re.IGNORECASE).strip(" :-#")
                    if value and not value.isupper():
                        fields[canonical.title()] = value
                        break
            if canonical.title() in fields:
                break

    date_match = DATE_RE.search("\n".join(lines))
    if date_match and "Date" not in fields:
        fields["Date"] = date_match.group(0)

    phone = fields.get("Phone", "")
    if "Due Date:" in phone:
        phone_value, due_value = re.split(r"\s+Due Date:\s*", phone, maxsplit=1, flags=re.IGNORECASE)
        fields["Phone"] = phone_value.strip()
        fields.setdefault("Due Date", due_value.strip())

    return fields


def _extract_amount_fields(lines: list[str], fields: dict[str, str]) -> None:
    for line in lines:
        lowered = line.lower()
        amounts = MONEY_RE.findall(line)
        if not amounts:
            continue

        amount = _clean_amount(amounts[-1])
        for canonical, labels in ALIASES.items():
            if canonical not in {"tax", "discount", "total", "gst amount"}:
                continue
            if any(label in lowered for label in labels):
                fields[canonical.title()] = amount

    if "Total" not in fields:
        parsed_amounts = []
        for line in lines:
            if any(skip in line.lower() for skip in ("phone", "mobile", "invoice", "bill no")):
                continue
            for amount in MONEY_RE.findall(line):
                try:
                    parsed_amounts.append(Decimal(_clean_amount(amount)))
                except InvalidOperation:
                    continue
        if parsed_amounts:
            fields["Total"] = str(max(parsed_amounts).quantize(Decimal("0.01")))


def _extract_line_rows(lines: list[str]) -> list[dict[str, str]]:
    rows = []
    skip = ("total", "subtotal", "tax", "gst", "discount", "invoice", "receipt", "date", "phone")

    for line in lines:
        lowered = line.lower()
        if any(word in lowered for word in skip):
            continue

        row = _parse_item_row(line)
        if not row:
            continue
        rows.append(row)

    return rows


def _parse_item_row(line: str) -> dict[str, str] | None:
    structured_match = ITEM_WITH_GST_RE.match(line)
    if structured_match:
        return {
            "S.No": structured_match.group("serial"),
            "Item": re.sub(r"\s{2,}", " ", structured_match.group("item").strip(" -:|")),
            "Qty": _clean_amount(structured_match.group("qty")).rstrip("0").rstrip("."),
            "Rate": _clean_amount(structured_match.group("rate")),
            "GST %": _clean_amount(structured_match.group("gst")).rstrip("0").rstrip("."),
            "Amount": _clean_amount(structured_match.group("amount")),
        }

    tokens = line.replace("|", " ").split()
    if len(tokens) < 2:
        return None

    numeric_tail: list[str] = []
    while tokens and MONEY_RE.fullmatch(tokens[-1].strip()):
        numeric_tail.insert(0, tokens.pop())

    if not numeric_tail or not tokens:
        return None

    if len(numeric_tail) > 3:
        tokens.extend(numeric_tail[:-3])
        numeric_tail = numeric_tail[-3:]

    description = re.sub(r"\s{2,}", " ", " ".join(tokens).strip(" -:|"))
    if len(description) < 2:
        return None

    row = {"Item": description}
    if len(numeric_tail) >= 3:
        row["Qty"] = _clean_amount(numeric_tail[-3]).rstrip("0").rstrip(".")
        row["Rate"] = _clean_amount(numeric_tail[-2])
        row["Amount"] = _clean_amount(numeric_tail[-1])
    elif len(numeric_tail) == 2:
        row["Rate"] = _clean_amount(numeric_tail[-2])
        row["Amount"] = _clean_amount(numeric_tail[-1])
    else:
        row["Amount"] = _clean_amount(numeric_tail[-1])

    return row


def _ordered_columns(source: list[dict[str, str]] | dict[str, str]) -> list[str]:
    rows = source if isinstance(source, list) else [source]
    discovered = []
    for row in rows:
        for column, value in row.items():
            if value and column not in discovered:
                discovered.append(column)

    preferred = [
        "Bill Name",
        "Invoice Number",
        "Date",
        "Customer",
        "Buyer",
        "Phone",
        "Address",
        "GST Number",
        "Due Date",
        "Place Of Supply",
        "S.No",
        "Item",
        "Description",
        "Qty",
        "Rate",
        "GST %",
        "Amount",
        "GST Amount",
        "Tax",
        "Discount",
        "Total",
        "Payment Method",
    ]
    ordered = [column for column in preferred if column in discovered]
    ordered.extend(column for column in discovered if column not in ordered)
    return ordered


def _normalize_rows(rows: list[dict[str, str]], columns: list[str]) -> list[dict[str, str]]:
    return [{column: row.get(column, "") for column in columns} for row in rows]


def _first_value(fields: dict[str, str], labels: tuple[str, ...]) -> str:
    for label in labels:
        value = fields.get(label)
        if value:
            return value
    return ""


def _bill_context(fields: dict[str, str]) -> dict[str, str]:
    context = {
        "Bill Name": _first_value(fields, ("Store Name", "Seller", "Vendor", "Company")),
        "Invoice Number": fields.get("Invoice Number", ""),
        "Date": fields.get("Date", ""),
        "Customer": fields.get("Customer", ""),
        "Buyer": fields.get("Buyer", ""),
        "Phone": fields.get("Phone", ""),
        "Address": fields.get("Address", ""),
        "GST Number": fields.get("Gst Number", ""),
        "Due Date": fields.get("Due Date", ""),
        "Place Of Supply": fields.get("Place Of Supply", ""),
        "GST Amount": fields.get("Gst Amount", ""),
        "Tax": fields.get("Tax", ""),
        "Discount": fields.get("Discount", ""),
        "Total": fields.get("Total", ""),
        "Payment Method": fields.get("Payment Method", ""),
    }
    return {key: value for key, value in context.items() if value}


def _attach_bill_context(rows: list[dict[str, str]], fields: dict[str, str]) -> list[dict[str, str]]:
    context = _bill_context(fields)
    if not context or not rows:
        return rows
    return [{**context, **row} for row in rows]


def _derive_bill_name(first_line: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 &.,'-]", " ", first_line)
    cleaned = re.sub(r"\b(?:tax\s+invoice|invoice|receipt|bill)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -:|")
    return cleaned


def _derive_bill_name_from_lines(lines: list[str]) -> str:
    skip_words = (
        "tax invoice",
        "invoice",
        "receipt",
        "bill",
        "bill to",
        "payment details",
        "terms",
        "description",
        "amount",
        "address",
        "date",
        "gstin",
    )
    for line in lines[:8]:
        lowered = line.lower()
        if ":" in line or any(word == lowered or word in lowered for word in skip_words):
            continue
        if re.search(r"[A-Za-z]", line):
            candidate = _derive_bill_name(line)
            if candidate:
                return candidate
    return _derive_bill_name(lines[0]) if lines else ""


def parse_dynamic_data(text: str, detected_type: str) -> dict:
    lines = [line.strip() for line in text.replace("\r", "\n").splitlines() if line.strip()]
    fields = _extract_label_value_fields(lines)
    _extract_amount_fields(lines, fields)

    if lines and "Store Name" not in fields:
        bill_name = _derive_bill_name_from_lines(lines)
        if bill_name:
            fields["Store Name"] = bill_name

    rows = _extract_line_rows(lines)
    if rows:
        rows = _attach_bill_context(rows, fields)
    if not rows and fields:
        rows = [fields.copy()]

    columns = _ordered_columns(rows if rows else fields)
    rows = _normalize_rows(rows, columns)

    return {
        "columns": columns,
        "rows": rows,
        "fields": fields,
        "detected_type": detected_type,
    }
