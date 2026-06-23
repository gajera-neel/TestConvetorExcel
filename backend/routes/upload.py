from pathlib import Path
from uuid import uuid4
from datetime import datetime

import pytesseract
from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from config.database import get_db
from parsers.dynamic_parser import parse_dynamic_data
from services.dashboard_service import build_dashboard
from services.document_service import extract_document
from services.bill_service import bill_to_record, save_bill
from services.temp_service import load_session, save_session


router = APIRouter()


def _build_upload_response(session: dict, db: Session) -> dict:
    return {
        "id": session["id"],
        "filename": session["filename"],
        "file_type": session["file_type"],
        "detected_type": session["detected_type"],
        "extracted_text": session["extracted_text"],
        "extracted_fields": {
            "columns": session.get("columns", []),
            "rows": session.get("rows", []),
            "fields": session.get("fields", {}),
            "detected_type": session.get("detected_type", "unknown"),
        },
        "confidence": session.get("confidence", 0),
        "logs": session.get("logs", []),
        "preview_url": session.get("preview_url", ""),
        "dashboard": build_dashboard(db),
        "history_record": session,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    upload_id = uuid4().hex
    safe_name = f"{upload_id}{extension}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(await file.read())

    try:
        document = extract_document(file_path, extension)
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Tesseract OCR is not installed or not available in PATH.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed on server: {exc}",
        ) from exc

    parsed = parse_dynamic_data(document["extracted_text"], document["detected_type"])
    if not document["extracted_text"].strip():
        document["logs"].append(
            "No readable text was extracted. Check image quality, crop/rotation, or server OCR installation."
        )
    session_payload = {
        "id": upload_id,
        "filename": file.filename,
        "stored_filename": safe_name,
        "file_path": str(file_path),
        "preview_url": f"/uploads/{safe_name}",
        "file_type": document["file_type"],
        "detected_type": document["detected_type"],
        "extracted_text": document["extracted_text"],
        "confidence": document["confidence"],
        "logs": document["logs"],
        "columns": parsed["columns"],
        "rows": parsed["rows"],
        "fields": parsed["fields"],
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
    }
    session = save_session(session_payload)
    bill = save_bill(db, session_payload)
    session["history_record"] = bill_to_record(bill)

    return _build_upload_response(session, db)


@router.post("/extract")
def extract_existing(payload: dict = Body(...), db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    file_path = Path(session["file_path"])
    extension = Path(session["filename"]).suffix.lower()
    document = extract_document(file_path, extension)
    parsed = parse_dynamic_data(document["extracted_text"], document["detected_type"])

    session.update(
        {
            "file_type": document["file_type"],
            "detected_type": document["detected_type"],
            "extracted_text": document["extracted_text"],
            "confidence": document["confidence"],
            "logs": document["logs"],
            "columns": parsed["columns"],
            "rows": parsed["rows"],
            "fields": parsed["fields"],
        }
    )
    save_session(session)
    save_bill(db, session)
    return _build_upload_response(session, db)
