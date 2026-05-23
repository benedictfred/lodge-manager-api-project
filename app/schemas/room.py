from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Union

from app.core.enums import BadgeTexts, BadgeVariants
from app.models.room import RoomStatus
from datetime import datetime


class RoomBase(BaseModel):
    room_no: str
    description: Optional[str] = None
    base_rent_price: int = Field(default=200000, ge=0)
    status: RoomStatus = RoomStatus.VACANT

    @field_validator('room_no', 'description')
    @classmethod
    def clean_strings(cls, value: str) -> Optional[str]:
        return value.strip().lower() if value else value


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    lodge_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomStatusCounts(BaseModel):
    occupied: int
    vacant: int
    maintenance: int

    model_config = ConfigDict(from_attributes=True)


class RoomUpdate(BaseModel):
    room_no: Optional[str] = None
    description: Optional[str] = None
    base_rent_price: Optional[int] = None
    status: Optional[RoomStatus] = None


class RoomGridSummary(BaseModel):
    lease_id: Optional[int] = None
    room_no: str
    badge_text: Union[BadgeTexts, RoomStatus]
    badge_variant: BadgeVariants
    main_display_text: str
    sub_display_text: str
