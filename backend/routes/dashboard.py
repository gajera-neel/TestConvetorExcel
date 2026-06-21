from fastapi import APIRouter

from services.dashboard_service import build_dashboard


router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
    return build_dashboard()
