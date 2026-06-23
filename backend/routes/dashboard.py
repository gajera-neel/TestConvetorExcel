from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from services.dashboard_service import get_bill_dashboard, get_global_dashboard


router = APIRouter()


@router.get("/dashboard")
def get_dashboard(bill_id: str | None = None, db: Session = Depends(get_db)):
    if bill_id:
        dashboard = get_bill_dashboard(db, bill_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Bill not found")
        return dashboard
    return get_global_dashboard(db)
