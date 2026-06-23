from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from services.dashboard_service import build_dashboard


router = APIRouter()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return build_dashboard(db)
