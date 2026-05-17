from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from app.core.enums import LeaseStatus
from app.schemas.room import RoomGridSummary


class LeaseBase(BaseModel):
    tenant_id: int
    room_id: int
    agreed_rent_amt: int = Field(..., ge=0)
    status: LeaseStatus = LeaseStatus.ACTIVE
    start_date: date
    end_date: date



class LeaseCreate(LeaseBase):
    total_amt_paid: int = Field(..., ge=0)


class LeaseResponse(LeaseBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class LeaseUpdate(BaseModel):
    tenant_id: Optional[int] = None
    room_id: Optional[int] = None
    agreed_rent_amt: Optional[int]  = Field(None, ge=0)
    status: Optional[LeaseStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class OccupiedRoomLeasesResponse(BaseModel):
    safe: list[RoomGridSummary]
    expiring: list[RoomGridSummary]
    overdue: list[RoomGridSummary]
    owing: list[RoomGridSummary]

