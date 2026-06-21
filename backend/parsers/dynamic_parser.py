import re
from decimal import Decimal, InvalidOperation


MONEY_RE = re.compile(r"(?:rs\.?|inr|usd|\$|₹)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\b")

ALIASES = {
    "store name": ("store", "vendor", "company", "shop", "merchant"),
    "invoice number": ("invoice no", "invoice number", "inv no", "bill no", "receipt no"),
    "date": ("date", "bill date", "invoice date"),
    "gst": ("gst", "gstin", "cgst", "sgst", "igst"),
    "phone": ("phone", "mobile", "contact"),
    "customer": ("customer", "customer name", "billed to"),
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
        if ":" in line:
            label, value = line.split(":", 1)
            if 2 <= len(label.strip()) <= 35 and value.strip():
                fields[_normalize_label(label)] = value.strip()

    for canonical, labels in ALIASES.items():
        if canonical.title() in fields:
            continue
        for line in lines:
            lowered = line.lower()
            for label in labels:
                if label in lowered:
                    value = re.sub(label, "", line, flags=re.IGNORECASE).strip(" :-#")
                    if value:
                        fields[canonical.title()] = value
                        break
            if canonical.title() in fields:
                break

    date_match = DATE_RE.search("\n".join(lines))
    if date_match and "Date" not in fields:
        fields["Date"] = date_match.group(0)

    return fields


def _extract_amount_fields(lines: list[str], fields: dict[str, str]) -> None:
    for line in lines:
        lowered = line.lower()
        amounts = MONEY_RE.findall(line)
        if not amounts:
            continue

        amount = _clean_amount(amounts[-1])
        for canonical, labels in ALIASES.items():
            if canonical not in {"tax", "discount", "total", "gst"}:
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

        amounts = MONEY_RE.findall(line)
        if not amounts:
            continue

        description = MONEY_RE.sub("", line).strip(" -:|")
        description = re.sub(r"\s{2,}", " ", description)
        if len(description) < 2:
            continue

        row = {
            "Item": description,
            "Amount": _clean_amount(amounts[-1]),
        }
        if len(amounts) > 1:
            row["Rate"] = _clean_amount(amounts[-2])
        qty_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:x|qty|pcs|pc)?\b", line, re.IGNORECASE)
        if qty_match:
            row["Qty"] = qty_match.group(1)
        rows.append(row)

    return rows[:50]


def parse_dynamic_data(text: str, detected_type: str) -> dict:
    lines = [line.strip() for line in text.replace("\r", "\n").splitlines() if line.strip()]
    fields = _extract_label_value_fields(lines)
    _extract_amount_fields(lines, fields)

    if lines and "Store Name" not in fields:
        first_line = re.sub(r"[^A-Za-z0-9 &.,'-]", "", lines[0]).strip()
        if first_line and not any(word in first_line.lower() for word in ("invoice", "receipt", "bill")):
            fields["Store Name"] = first_line

    rows = _extract_line_rows(lines)
    if not rows and fields:
        rows = [fields.copy()]

    columns = sorted({column for row in rows for column in row.keys()} | set(fields.keys()))

    return {
        "columns": columns,
        "rows": rows,
        "fields": fields,
        "detected_type": detected_type,
    }
