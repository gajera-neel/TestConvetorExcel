from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from config.database import get_db
from services.excel_service import create_custom_excel, create_excel_report
from services.temp_service import latest_session, load_session


router = APIRouter()


@router.get("/download-excel")
def download_excel(db: Session = Depends(get_db)):
    report_path = create_excel_report(db)
    return FileResponse(
        report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=report_path.name,
    )


@router.post("/generate-excel")
def generate_excel(payload: dict = Body(default={})):
    session = None
    if payload.get("session_id"):
        session = load_session(payload["session_id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = latest_session()

    rows = payload.get("rows") or (session or {}).get("rows") or []
    columns = payload.get("columns") or (session or {}).get("columns") or []

    if not rows:
        raise HTTPException(status_code=400, detail="No rows available for Excel export")

    report_path = create_custom_excel(rows=rows, columns=columns)
    return FileResponse(
        report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=report_path.name,
    )
