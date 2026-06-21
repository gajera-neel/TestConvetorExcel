from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from config import UPLOAD_DIR
from routes.dashboard import router as dashboard_router
from routes.excel import router as excel_router
from routes.upload import router as upload_router
from services.excel_service import create_custom_excel
from services.temp_service import latest_session, load_session

app = FastAPI(title="Document Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(dashboard_router)
app.include_router(excel_router)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Document Intelligence API is running"}


@app.post("/generate-excel")
def generate_excel(payload: dict = Body(default={})):
    session = load_session(payload["session_id"]) if payload.get("session_id") else latest_session()
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
