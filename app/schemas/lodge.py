from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.schemas.room import RoomResponse
from app.schemas.tenantprofile import TenantProfileResponse


class LodgeBase(BaseModel):
    name: str
    address: str

    @field_validator('name', 'address')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()


class LodgeCreate(LodgeBase):
    pass



class LodgeResponse(LodgeBase):
    id: int
    landlord_id: int
    created_at: datetime
    is_active: bool

    model_config = {'from_attributes': True}


class LodgeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

    @field_validator('name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.lower()
