from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd
from sqlalchemy.orm import Session

from services.bill_service import list_bills


def _amount_from_record(record: dict) -> Decimal:
    fields = record.get("fields", {})
    rows = record.get("rows") or []
    value = fields.get("Total") or fields.get("Amount") or fields.get("Grand Total")
    if not value and rows:
        row_amounts = [_decimal_from_value(row.get("Amount") or row.get("Total") or "0") for row in rows]
        return sum(row_amounts, Decimal("0"))
    value = value or "0"
    return _decimal_from_value(value)


def _decimal_from_value(value: object) -> Decimal:
    cleaned = str(value).replace(",", "").replace("₹", "").replace("$", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def _format_money(value: Decimal) -> str:
    return f"₹{value.quantize(Decimal('0.01'))}"


def _vendor_from_record(record: dict) -> str:
    fields = record.get("fields", {})
    return fields.get("Store Name") or fields.get("Vendor") or fields.get("Seller") or fields.get("Company") or "Unknown Vendor"


def _recent_upload(record: dict) -> dict:
    amount = _amount_from_record(record)
    return {
        **record,
        "vendor": _vendor_from_record(record),
        "amount": _format_money(amount),
        "rows_count": len(record.get("rows") or []),
    }


def build_dashboard(db: Session) -> dict:
    history = list_bills(db)
    today = date.today().isoformat()

    if not history:
        return {
            "metrics": {
                "uploads": 0,
                "bills": 0,
                "success_rate": 0,
                "total_records": 0,
                "total_uploads": 0,
                "total_bills": 0,
                "total_amount": "₹0.00",
                "average_bill_amount": "₹0.00",
                "highest_bill_amount": "₹0.00",
                "unique_vendors": 0,
                "todays_uploads": 0,
            },
            "uploads_by_day": [],
            "amount_trend": [],
            "bill_categories": [],
            "extraction_activity": [],
            "file_types": [],
            "data_volume": [],
            "top_vendors": [],
            "recent_uploads": [],
        }

    frame = pd.DataFrame(history)
    frame["day"] = frame["uploaded_at"].str.slice(0, 10)
    frame["amount"] = [_amount_from_record(record) for record in history]
    frame["vendor"] = [_vendor_from_record(record) for record in history]

    uploads_by_day = (
        frame.groupby("day")
        .size()
        .reset_index(name="count")
        .sort_values("day")
        .to_dict(orient="records")
    )
    amount_trend = (
        frame.groupby("day")["amount"]
        .sum()
        .reset_index(name="amount")
        .sort_values("day")
        .to_dict(orient="records")
    )
    bill_categories = (
        frame.groupby("detected_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .to_dict(orient="records")
    )

    total_bills = frame["detected_type"].isin(["bill", "invoice", "receipt"]).sum()
    total_amount = sum(frame["amount"], Decimal("0"))
    amount_values = [amount for amount in frame["amount"].tolist() if amount > 0]
    average_amount = (total_amount / len(amount_values)) if amount_values else Decimal("0")
    highest_amount = max(amount_values, default=Decimal("0"))
    top_vendors = (
        frame[frame["vendor"] != "Unknown Vendor"]
        .groupby("vendor")["amount"]
        .sum()
        .reset_index(name="amount")
        .sort_values("amount", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )

    return {
        "metrics": {
            "uploads": int(len(history)),
            "bills": int(total_bills),
            "success_rate": int(round((frame["confidence"].fillna(0).astype(float).mean() or 0) * 100)),
            "total_records": int(sum(len(record.get("rows") or []) for record in history)),
            "total_uploads": int(len(history)),
            "total_bills": int(total_bills),
            "total_amount": _format_money(total_amount),
            "average_bill_amount": _format_money(average_amount),
            "highest_bill_amount": _format_money(highest_amount),
            "unique_vendors": int(frame["vendor"].replace("Unknown Vendor", pd.NA).dropna().nunique()),
            "todays_uploads": int((frame["day"] == today).sum()),
        },
        "uploads_by_day": uploads_by_day,
        "amount_trend": [{"label": item["day"], "value": float(item["amount"])} for item in amount_trend],
        "bill_categories": bill_categories,
        "extraction_activity": [{"label": item["day"], "value": item["count"]} for item in uploads_by_day],
        "file_types": (
            frame.groupby("file_type").size().reset_index(name="value").rename(columns={"file_type": "label"}).to_dict(orient="records")
        ),
        "data_volume": [
            {"label": "Rows", "value": int(sum(len(record.get("rows") or []) for record in history))},
            {"label": "Columns", "value": int(max((len(record.get("columns") or []) for record in history), default=0))},
            {"label": "Uploads", "value": int(len(history))},
        ],
        "top_vendors": [{"label": item["vendor"], "value": float(item["amount"])} for item in top_vendors],
        "recent_uploads": [_recent_upload(record) for record in history[-8:][::-1]],
    }
