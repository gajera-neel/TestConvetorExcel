from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from services.bill_service import delete_bill, get_bill, import_old_temp_json, list_bills


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
    if not delete_bill(db, bill_id):
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"deleted": True, "id": bill_id}


@router.post("/migrate-old-json")
def migrate_old_json(db: Session = Depends(get_db)):
    imported = import_old_temp_json(db)
    return {"imported": imported}
