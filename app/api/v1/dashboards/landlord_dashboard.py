from dataclasses import dataclass, Field
from enum import Enum
from typing import Annotated, List, Union

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.api.deps import get_landlord_user, get_db
from app.core.enums import RoomStatus, BadgeTexts
from app.models.user import User
from app.schemas import dashboard as schema_dashboard
from app.services import dashboard_service


router = APIRouter()




@router.get('/me/landlord/{lodge_id}', response_model=schema_dashboard.LandlordDashboardStats)
def get_landlord_dashboard(
        lodge_id: int,
        room_statuses: list[RoomStatus] = Query(default=[]),
        financial_filters: list[BadgeTexts] = Query(default=[]),
        skip: int | None = None,
        limit: int | None = None,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user),

):
    #goal: to get a list of landlord dashboard stats with
    #financial summary, total entities count, dictionary of dashboard rooms categories
    # that match a specific filter and is paginated
    #does the lodge exist and is owned by the landlord??
    return dashboard_service.get_landlord_dashboard(db, lodge_id=lodge_id, landlord_id=landlord_user.id)