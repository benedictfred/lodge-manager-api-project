from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_landlord_user, get_db
from app.models.user import User
from app.schemas import dashboard as schema_dashboard
from app.services import dashboard_service


router = APIRouter()


@router.get('/me/landlord/{lodge_id}', response_model=schema_dashboard.LandlordDashboardStats)
def get_landlord_dashboard(
        lodge_id: int,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    #does the lodge exist and is owned by the landlord??
    return dashboard_service.get_landlord_dashboard(db, lodge_id=lodge_id, landlord_id=landlord_user.id)