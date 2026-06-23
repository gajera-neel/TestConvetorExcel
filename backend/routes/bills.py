from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from services.bill_service import get_bill, import_old_temp_json, list_bills
from services.dashboard_service import delete_bill_and_refresh


router = APIRouter()


@router.get("/bills")
def get_bills(db: Session = Depends(get_db)):
    return {"bills": list_bills(db)}


@router.get("/bill/{bill_id}")
def get_bill_by_id(bill_id: str, db: Session = Depends(get_db)):
    bill = get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.delete("/bill/{bill_id}")
def delete_bill_by_id(bill_id: str, db: Session = Depends(get_db)):
    dashboard = delete_bill_and_refresh(db, bill_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"deleted": True, "id": bill_id, "dashboard": dashboard}


@router.post("/migrate-old-json")
def migrate_old_json(db: Session = Depends(get_db)):
    imported = import_old_temp_json(db)
    return {"imported": imported}
