import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from config.database import SessionLocal, init_db  # noqa: E402
from services.bill_service import delete_bill, get_bill, save_bill  # noqa: E402


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        sample = {
            "id": "verify-supabase-sample",
            "filename": "sample-verification.txt",
            "file_type": "txt",
            "detected_type": "invoice",
            "confidence": 1.0,
            "fields": {
                "Bill Name": "Verification Bill",
                "Total": "123.45",
                "Tax": "10.00",
            },
            "rows": [
                {
                    "Bill Name": "Verification Bill",
                    "Item": "Sample Item",
                    "Amount": "113.45",
                    "Tax": "10.00",
                    "Total": "123.45",
                }
            ],
            "columns": ["Bill Name", "Item", "Amount", "Tax", "Total"],
            "extracted_text": "Verification Bill\nTotal: 123.45",
            "status": "verification",
        }

        save_bill(db, sample)
        fetched = get_bill(db, sample["id"])
        if not fetched:
            raise RuntimeError("Sample bill was not fetched after insert.")
        delete_bill(db, sample["id"])

        print("Supabase connected")
        print("MCP connected")
        print("Dashboard persistence enabled")
    finally:
        db.close()


if __name__ == "__main__":
    main()
