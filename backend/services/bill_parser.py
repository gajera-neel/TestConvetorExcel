import re
from decimal import Decimal, InvalidOperation


MONEY_RE = re.compile(r"(?:rs\.?|inr|usd|\$|₹)?\s*([0-9]{1,3}(?:[, ]?[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", re.IGNORECASE)
DATE_RE = re.compile(
    r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})\b",
    re.IGNORECASE,
)
INVOICE_RE = re.compile(
    r"\b(?:invoice|inv|bill|receipt|voucher)\s*(?:no|number|#|:)?\s*[:#-]?\s*([A-Z0-9][A-Z0-9\-\/]{2,})",
    re.IGNORECASE,
)

FIELD_LABELS = {
    "subtotal": ("subtotal", "sub total", "sub-total", "taxable amount", "amount before tax"),
    "tax": ("tax", "gst", "cgst", "sgst", "igst", "vat"),
    "total": ("grand total", "net total", "total amount", "amount due", "balance due", "total"),
}


def _normalize_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.replace("\r", "\n").splitlines())


def _parse_money(value: str) -> str:
    cleaned = value.replace(",", "").replace(" ", "")
    try:
        return str(Decimal(cleaned).quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        return ""


def _find_currency(text: str) -> str:
    lowered = text.lower()
    if "₹" in text or "inr" in lowered or "rs" in lowered:
        return "INR"
    if "$" in text or "usd" in lowered:
        return "USD"
    return ""


def _find_labeled_amount(lines: list[str], labels: tuple[str, ...]) -> str:
    matches = []
    for line in lines:
        lowered = line.lower()
        if any(label in lowered for label in labels):
            amounts = MONEY_RE.findall(line)
            if amounts:
                matches.append(_parse_money(amounts[-1]))
    return next((amount for amount in reversed(matches) if amount), "")


def _find_total(lines: list[str]) -> str:
    labeled_total = _find_labeled_amount(lines, FIELD_LABELS["total"])
    if labeled_total:
        return labeled_total

    amounts = []
    for line in lines:
        lowered = line.lower()
        if any(skip in lowered for skip in ("phone", "mobile", "invoice", "bill no")):
            continue
        for amount in MONEY_RE.findall(line):
            parsed = _parse_money(amount)
            if parsed:
                amounts.append(Decimal(parsed))

    return str(max(amounts).quantize(Decimal("0.01"))) if amounts else ""


def _find_vendor(lines: list[str]) -> str:
    skip_words = (
        "invoice",
        "bill",
        "receipt",
        "date",
        "gst",
        "tax",
        "total",
        "qty",
        "amount",
        "subtotal",
    )
    for line in lines[:8]:
        cleaned = re.sub(r"[^A-Za-z0-9 &.,'-]", "", line).strip()
        if len(cleaned) >= 3 and not any(word in cleaned.lower() for word in skip_words):
            return cleaned
    return ""


def _find_invoice_number(text: str) -> str:
    match = INVOICE_RE.search(text)
    return match.group(1).strip() if match else ""


def _find_date(text: str) -> str:
    match = DATE_RE.search(text)
    return match.group(0).strip() if match else ""


def _parse_line_items(lines: list[str]) -> list[dict[str, str]]:
    items = []
    skip_words = (
        "subtotal",
        "total",
        "tax",
        "gst",
        "cash",
        "change",
        "balance",
        "amount due",
        "invoice",
        "receipt",
        "bill no",
        "bill number",
        "date",
        "phone",
        "mobile",
    )

    for line in lines:
        lowered = line.lower()
        if any(word in lowered for word in skip_words):
            continue

        amounts = MONEY_RE.findall(line)
        if not amounts:
            continue

        total = _parse_money(amounts[-1])
        description = MONEY_RE.sub("", line).strip(" -:|")
        description = re.sub(r"\s{2,}", " ", description)

        if len(description) < 2 or not total:
            continue

        qty_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:x|pcs|pc|qty)?\b", line, re.IGNORECASE)
        items.append(
            {
                "description": description,
                "quantity": qty_match.group(1) if qty_match else "",
                "unit_price": _parse_money(amounts[-2]) if len(amounts) > 1 else "",
                "total": total,
            }
        )

    return items[:30]


def parse_bill(text: str) -> dict:
    normalized = _normalize_text(text)
    lines = [line for line in normalized.splitlines() if line]

    subtotal = _find_labeled_amount(lines, FIELD_LABELS["subtotal"])
    tax = _find_labeled_amount(lines, FIELD_LABELS["tax"])
    total = _find_total(lines)

    return {
        "vendor": _find_vendor(lines),
        "invoice_number": _find_invoice_number(normalized),
        "date": _find_date(normalized),
        "currency": _find_currency(normalized),
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "line_items": _parse_line_items(lines),
        "raw_text": normalized,
    }
