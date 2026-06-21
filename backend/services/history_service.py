import json
from datetime import datetime
from pathlib import Path

from config import HISTORY_FILE


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(history: list[dict]) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def add_history_record(record: dict) -> dict:
    history = load_history()
    record = {
        "id": record.get("id"),
        "filename": record.get("filename", ""),
        "file_type": record.get("file_type", ""),
        "detected_type": record.get("detected_type", ""),
        "confidence": record.get("confidence", 0),
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "fields": record.get("fields", {}),
        "rows": record.get("rows", []),
        "extracted_text": record.get("extracted_text", ""),
        "columns": record.get("columns", []),
        "file_path": record.get("file_path", ""),
        "preview_url": record.get("preview_url", ""),
    }
    history.append(record)
    save_history(history)
    return record


def get_latest_record() -> dict | None:
    history = load_history()
    return history[-1] if history else None
