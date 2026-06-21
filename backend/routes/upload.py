from pathlib import Path
from uuid import uuid4

import pytesseract
from fastapi import APIRouter, Body, File, HTTPException, UploadFile

from config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from parsers.dynamic_parser import parse_dynamic_data
from services.dashboard_service import build_dashboard
from services.document_service import extract_document
from services.history_service import add_history_record
from services.temp_service import load_session, save_session


router = APIRouter()


def _build_upload_response(session: dict) -> dict:
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
        "dashboard": build_dashboard(),
        "history_record": session,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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

    parsed = parse_dynamic_data(document["extracted_text"], document["detected_type"])
    session = save_session(
        {
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
        }
    )
    record = add_history_record(
        {
            "id": upload_id,
            "filename": file.filename,
            "file_type": document["file_type"],
            "detected_type": document["detected_type"],
            "confidence": document["confidence"],
            "fields": parsed["fields"],
            "rows": parsed["rows"],
            "columns": parsed["columns"],
            "file_path": str(file_path),
            "preview_url": f"/uploads/{safe_name}",
            "extracted_text": document["extracted_text"],
        }
    )
    session["history_record"] = record

    return _build_upload_response(session)


@router.post("/extract")
def extract_existing(payload: dict = Body(...)):
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
    return _build_upload_response(session)
