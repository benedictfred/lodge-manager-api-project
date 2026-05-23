from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_landlord_user
from app.models.user import User
from app.schemas import user as schema_user
from app.schemas import tenantprofile as schema_tenant
from app.schemas.dashboard import LandlordDashboardStats

from app.services import user_service, dashboard_service
from app.services.tenant_services import sign_up_tenant
from app.core.exceptions import UserAlreadyExistError


router = APIRouter()


@router.get('/me/landlord/{lodge_id}', response_model=LandlordDashboardStats)
def get_landlord_dashboard(
        db: Session,
        lodge_id: int,
        landlord_user: User = Depends(get_landlord_user)
):
    #does the lodge exist and is owned by the landlord??
    return dashboard_service.get_landlord_dashboard(db, lodge_id=lodge_id, landlord_id=landlord_user.id, )
    pass