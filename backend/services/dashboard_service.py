from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd
from sqlalchemy.orm import Session

from parsers.dynamic_parser import parse_dynamic_data
from services.bill_service import _amounts, calculate_bill_totals, delete_bill, get_bill, list_bills


def _corrected_fields_and_rows(record: dict) -> tuple[dict, list[dict]]:
    text = str(record.get("extracted_text") or "").strip()
    if text:
        try:
            parsed = parse_dynamic_data(text, record.get("detected_type") or "Bill")
            fields = parsed.get("fields") or {}
            rows = parsed.get("rows") or []
            if fields or rows:
                return fields, rows
        except Exception:
            pass
    return record.get("fields", {}) or {}, record.get("rows") or []


def _amount_from_record(record: dict) -> Decimal:
    fields, rows = _corrected_fields_and_rows(record)
    _, _, total = _amounts(fields, rows)
    if total:
        return total
    value = fields.get("Total") or fields.get("Grand Total") or fields.get("Amount") or "0"
    return _decimal_from_value(value)


def _tax_from_record(record: dict) -> Decimal:
    fields, rows = _corrected_fields_and_rows(record)
    _, tax, _ = _amounts(fields, rows)
    return tax


def _calculation_audit(record: dict) -> dict:
    fields, rows = _corrected_fields_and_rows(record)
    totals = calculate_bill_totals(fields, rows)
    return {
        "subtotal": _format_money(totals["subtotal"]),
        "tax": _format_money(totals["tax"]),
        "discount": _format_money(totals["discount"]),
        "total": _format_money(totals["total"]),
        "expected_total": _format_money(totals["expected_total"]),
        "difference": _format_money(totals["difference"]),
        "is_balanced": totals["is_balanced"],
        "issues": totals["issues"],
        "sources": totals["sources"],
        "raw_fields": fields,
        "raw_rows": rows,
    }


def _decimal_from_value(value: object) -> Decimal:
    cleaned = str(value).replace(",", "").replace("₹", "").replace("$", "").replace("Rs.", "").strip()
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _format_money(value: Decimal) -> str:
    return f"₹{value.quantize(Decimal('0.01'))}"


def _vendor_from_record(record: dict) -> str:
    if record.get("vendor"):
        return record["vendor"]
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


def _uploaded_bill(record: dict) -> dict:
    audit = _calculation_audit(record)
    return {
        "id": record.get("id", ""),
        "filename": record.get("filename", "Untitled document"),
        "bill_name": record.get("bill_name") or record.get("fields", {}).get("Bill Name") or record.get("filename", ""),
        "uploaded_at": record.get("uploaded_at", ""),
        "file_type": record.get("file_type", ""),
        "detected_type": record.get("detected_type", ""),
        "amount": _format_money(_amount_from_record(record)),
        "vendor": _vendor_from_record(record),
        "status": record.get("status", "processed"),
        "confidence": record.get("confidence", 0),
        "rows_count": len(record.get("rows") or []),
        "calculation_status": "balanced" if audit["is_balanced"] else "needs_review",
        "calculation_issues": audit["issues"],
    }


def _empty_global_dashboard() -> dict:
    return {
        "mode": "global",
        "metrics": {
            "uploads": 0,
            "bills": 0,
            "success_rate": 0,
            "total_records": 0,
            "total_uploads": 0,
            "total_bills": 0,
            "total_amount": "₹0.00",
            "total_tax": "₹0.00",
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
        "uploaded_bills": [],
    }


def get_global_dashboard(db: Session) -> dict:
    history = list_bills(db)
    today = date.today().isoformat()

    if not history:
        return _empty_global_dashboard()

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
    total_tax = sum((_tax_from_record(record) for record in history), Decimal("0"))
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
        "mode": "global",
        "metrics": {
            "uploads": int(len(history)),
            "bills": int(total_bills),
            "success_rate": int(round((frame["confidence"].fillna(0).astype(float).mean() or 0) * 100)),
            "total_records": int(sum(len(record.get("rows") or []) for record in history)),
            "total_uploads": int(len(history)),
            "total_bills": int(total_bills),
            "total_amount": _format_money(total_amount),
            "total_tax": _format_money(total_tax),
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
        "recent_uploads": [_recent_upload(record) for record in history[:8]],
        "uploaded_bills": [_uploaded_bill(record) for record in history],
        "calculation_issues": [
            {
                "id": record.get("id"),
                "filename": record.get("filename"),
                "audit": audit,
            }
            for record in history
            for audit in [_calculation_audit(record)]
            if not audit["is_balanced"]
        ],
    }


def get_bill_dashboard(db: Session, bill_id: str) -> dict | None:
    record = get_bill(db, bill_id)
    if not record:
        return None

    fields = record.get("fields") or {}
    rows = record.get("rows") or []
    columns = record.get("columns") or []
    amount = _amount_from_record(record)
    tax = _tax_from_record(record)
    audit = _calculation_audit(record)
    confidence = float(record.get("confidence") or 0)

    amount_breakdown = [
        {"label": "Amount", "value": float(amount)},
        {"label": "Tax", "value": float(tax)},
    ]
    row_summary = [
        {"label": "Rows", "value": len(rows)},
        {"label": "Columns", "value": len(columns)},
        {"label": "Fields", "value": len([value for value in fields.values() if value])},
    ]

    return {
        "mode": "single",
        "bill_id": bill_id,
        "metrics": {
            "uploads": 1,
            "bills": 1 if str(record.get("detected_type", "")).lower() in {"bill", "invoice", "receipt"} else 0,
            "success_rate": int(round(confidence * 100)),
            "total_records": len(rows),
            "total_uploads": 1,
            "total_bills": 1,
            "total_amount": _format_money(amount),
            "total_tax": _format_money(tax),
            "average_bill_amount": _format_money(amount),
            "highest_bill_amount": _format_money(amount),
            "unique_vendors": 1 if _vendor_from_record(record) != "Unknown Vendor" else 0,
            "todays_uploads": 1 if str(record.get("uploaded_at", "")).startswith(date.today().isoformat()) else 0,
        },
        "bill": {
            **_uploaded_bill(record),
            "fields": fields,
            "rows": rows,
            "columns": columns,
            "extracted_text": record.get("extracted_text", ""),
            "preview_url": record.get("preview_url", ""),
            "invoice_number": record.get("invoice_number", ""),
            "bill_date": record.get("bill_date", ""),
            "customer": record.get("customer", ""),
            "tax": _format_money(tax),
            "total": _format_money(amount),
            "calculation": audit,
            "raw_json": record,
        },
        "summary": [
            {"label": "Vendor", "value": _vendor_from_record(record)},
            {"label": "Upload Date", "value": record.get("uploaded_at", "")},
            {"label": "File Type", "value": record.get("file_type", "")},
            {"label": "Status", "value": record.get("status", "processed")},
            {"label": "Confidence", "value": f"{int(round(confidence * 100))}%"},
            {"label": "Calculation Status", "value": "Balanced" if audit["is_balanced"] else "Needs Review"},
        ],
        "amount_trend": [{"label": record.get("bill_name") or record.get("filename", "Bill"), "value": float(amount)}],
        "bill_categories": [{"label": record.get("detected_type") or "document", "value": 1}],
        "extraction_activity": row_summary,
        "file_types": [{"label": record.get("file_type") or "file", "value": 1}],
        "data_volume": row_summary,
        "top_vendors": [{"label": _vendor_from_record(record), "value": float(amount)}],
        "amount_breakdown": amount_breakdown,
        "calculation_issues": [] if audit["is_balanced"] else [{"id": bill_id, "filename": record.get("filename"), "audit": audit}],
        "recent_uploads": [_recent_upload(record)],
        "uploaded_bills": [_uploaded_bill(item) for item in list_bills(db)],
    }


def delete_bill_and_refresh(db: Session, bill_id: str) -> dict | None:
    if not delete_bill(db, bill_id):
        return None
    return get_global_dashboard(db)


def build_dashboard(db: Session) -> dict:
    return get_global_dashboard(db)
