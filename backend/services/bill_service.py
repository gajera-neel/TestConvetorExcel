import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from config import HISTORY_FILE, TEMP_DIR
from models.bill import Bill


def _decimal(value: object) -> Decimal:
    cleaned = str(value or "0").replace(",", "").replace("₹", "").replace("$", "").strip()
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


def _field_value(fields: dict, labels: tuple[str, ...]) -> str:
    for label in labels:
        value = fields.get(label)
        if value:
            return str(value)
    return ""


def _sum_rows(rows: list[dict], labels: tuple[str, ...]) -> Decimal:
    total = Decimal("0.00")
    for row in rows:
        total += _decimal(_field_value(row, labels))
    return total


def _bill_name(fields: dict, filename: str) -> str:
    return (
        _field_value(fields, ("Bill Name", "Store Name", "Seller", "Vendor", "Company"))
        or filename
        or "Unknown Bill"
    )


def _vendor(fields: dict, filename: str) -> str:
    return _bill_name(fields, filename)


def _amounts(fields: dict, rows: list[dict]) -> tuple[Decimal, Decimal, Decimal]:
    amount = _sum_rows(rows, ("Amount", "Total"))
    tax = _decimal(_field_value(fields, ("Tax", "GST Amount", "Gst Amount", "Gst", "CGST", "SGST", "IGST")))
    total = _decimal(_field_value(fields, ("Total", "Grand Total", "Net Total", "Amount")))

    if amount == Decimal("0.00"):
        amount = total
    if total == Decimal("0.00"):
        total = amount + tax

    return amount, tax, total


def bill_to_record(bill: Bill) -> dict:
    raw = bill.raw_json or {}
    return {
        **raw,
        "id": bill.id,
        "bill_name": bill.bill_name,
        "filename": bill.filename,
        "file_type": bill.file_type,
        "detected_type": bill.detected_type,
        "confidence": float(bill.confidence),
        "vendor": bill.vendor,
        "invoice_number": bill.invoice_number,
        "bill_date": bill.bill_date,
        "customer": bill.customer,
        "buyer": bill.buyer,
        "phone": bill.phone,
        "gst_number": bill.gst_number,
        "amount": str(bill.amount),
        "tax": str(bill.tax),
        "gst_amount": str(bill.gst_amount),
        "discount": str(bill.discount),
        "total": str(bill.total),
        "payment_method": bill.payment_method,
        "rows_count": bill.rows_count,
        "columns": bill.columns_json or raw.get("columns", []),
        "rows": bill.rows_json or raw.get("rows", []),
        "fields": bill.fields_json or raw.get("fields", {}),
        "extracted_text": bill.extracted_text,
        "preview_url": bill.preview_url,
        "file_path": bill.file_path,
        "uploaded_at": bill.upload_date.isoformat(timespec="seconds"),
        "status": bill.status,
    }


def save_bill(db: Session, record: dict) -> Bill:
    fields = record.get("fields") or {}
    rows = record.get("rows") or []
    amount, tax, total = _amounts(fields, rows)
    gst_amount = _decimal(_field_value(fields, ("GST Amount", "Gst Amount", "Gst", "CGST", "SGST", "IGST")))
    discount = _decimal(_field_value(fields, ("Discount", "Disc")))
    upload_date = record.get("uploaded_at")
    parsed_upload_date = (
        datetime.fromisoformat(upload_date) if isinstance(upload_date, str) and upload_date else datetime.utcnow()
    )

    bill = Bill(
        id=record["id"],
        bill_name=_bill_name(fields, record.get("filename", "")),
        filename=record.get("filename", ""),
        file_type=record.get("file_type", ""),
        detected_type=record.get("detected_type", ""),
        confidence=_decimal(record.get("confidence", 0)),
        vendor=_vendor(fields, record.get("filename", "")),
        invoice_number=_field_value(fields, ("Invoice Number", "Bill Number", "Receipt Number")),
        bill_date=_field_value(fields, ("Date", "Invoice Date", "Bill Date")),
        customer=_field_value(fields, ("Customer", "Customer Name")),
        buyer=_field_value(fields, ("Buyer", "Billed To", "Bill To")),
        phone=_field_value(fields, ("Phone", "Mobile", "Contact")),
        gst_number=_field_value(fields, ("GST Number", "Gst Number", "GSTIN", "Gstin")),
        amount=amount,
        tax=tax,
        gst_amount=gst_amount,
        discount=discount,
        total=total,
        payment_method=_field_value(fields, ("Payment Method", "Paid By", "Mode")),
        rows_count=len(rows),
        columns_json=record.get("columns") or [],
        rows_json=rows,
        fields_json=fields,
        extracted_text=record.get("extracted_text", ""),
        preview_url=record.get("preview_url", ""),
        file_path=record.get("file_path", ""),
        upload_date=parsed_upload_date,
        raw_json=record,
        status=record.get("status", "processed"),
    )
    bill = db.merge(bill)
    db.commit()
    db.refresh(bill)
    return bill


def list_bills(db: Session) -> list[dict]:
    bills = db.query(Bill).order_by(Bill.upload_date.desc()).all()
    return [bill_to_record(bill) for bill in bills]


def get_bill(db: Session, bill_id: str) -> dict | None:
    bill = db.get(Bill, bill_id)
    return bill_to_record(bill) if bill else None


def delete_bill(db: Session, bill_id: str) -> bool:
    bill = db.get(Bill, bill_id)
    if not bill:
        return False
    db.delete(bill)
    db.commit()
    return True


def _load_json_file(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def import_old_temp_json(db: Session) -> int:
    imported = 0
    history = _load_json_file(HISTORY_FILE)
    if isinstance(history, list):
        for record in history:
            if isinstance(record, dict) and record.get("id"):
                save_bill(db, record)
                imported += 1

    for path in TEMP_DIR.glob("*.json"):
        if path.name == "history.json":
            continue
        session = _load_json_file(path)
        if isinstance(session, dict) and session.get("id"):
            save_bill(db, session)
            imported += 1

    return imported
