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
        "amount": str(bill.amount),
        "tax": str(bill.tax),
        "total": str(bill.total),
        "uploaded_at": bill.upload_date.isoformat(timespec="seconds"),
        "status": bill.status,
    }


def save_bill(db: Session, record: dict) -> Bill:
    fields = record.get("fields") or {}
    rows = record.get("rows") or []
    amount, tax, total = _amounts(fields, rows)
    upload_date = record.get("uploaded_at")
    parsed_upload_date = (
        datetime.fromisoformat(upload_date) if isinstance(upload_date, str) and upload_date else datetime.utcnow()
    )

    bill = Bill(
        id=record["id"],
        bill_name=_bill_name(fields, record.get("filename", "")),
        amount=amount,
        tax=tax,
        total=total,
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
