from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd

from services.history_service import load_history


def _amount_from_record(record: dict) -> Decimal:
    fields = record.get("fields", {})
    value = fields.get("Total") or fields.get("Amount") or fields.get("Grand Total") or "0"
    cleaned = str(value).replace(",", "").replace("₹", "").replace("$", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def build_dashboard() -> dict:
    history = load_history()
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
                "total_amount": "0.00",
                "unique_vendors": 0,
                "todays_uploads": 0,
            },
            "uploads_by_day": [],
            "amount_trend": [],
            "bill_categories": [],
            "extraction_activity": [],
            "file_types": [],
            "data_volume": [],
            "recent_uploads": [],
        }

    frame = pd.DataFrame(history)
    frame["day"] = frame["uploaded_at"].str.slice(0, 10)
    frame["amount"] = [_amount_from_record(record) for record in history]
    frame["vendor"] = [record.get("fields", {}).get("Store Name") or record.get("fields", {}).get("Vendor") or "" for record in history]

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

    return {
        "metrics": {
            "uploads": int(len(history)),
            "bills": int(total_bills),
            "success_rate": int(round((frame["confidence"].fillna(0).astype(float).mean() or 0) * 100)),
            "total_records": int(sum(len(record.get("rows") or []) for record in history)),
            "total_uploads": int(len(history)),
            "total_bills": int(total_bills),
            "total_amount": str(total_amount.quantize(Decimal("0.01"))),
            "unique_vendors": int(frame["vendor"].replace("", pd.NA).dropna().nunique()),
            "todays_uploads": int((frame["day"] == today).sum()),
        },
        "uploads_by_day": uploads_by_day,
        "amount_trend": [{"day": item["day"], "amount": str(item["amount"])} for item in amount_trend],
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
        "recent_uploads": history[-8:][::-1],
    }
