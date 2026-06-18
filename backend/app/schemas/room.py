"""
Pydantic schemas for the room domain.

This module contains schemas used to represent, create, and update rooms,
as well as summarizing room statuses for dashboards.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Union
from app.core.enums import BadgeTexts, BadgeVariants
from app.core.enums import  RoomStatus
from datetime import datetime


class RoomBase(BaseModel):
    """
    Base schema for a room.

    Attributes:
        room_no (str): The room number or identifier.
        description (Optional[str]): The description of the room.
        base_rent_price (int): The base rental price.
        status (RoomStatus): The current status of the room.
    """
    room_no: str
    description: Optional[str] = None
    base_rent_price: int = Field(default=200000, ge=0)


    @field_validator('room_no', 'description')
    @classmethod
    def clean_strings(cls, value: str) -> Optional[str]:
        return value.strip().lower() if value else value


class RoomCreate(RoomBase):
    lodge_id: int
    pass


class RoomResponse(RoomCreate):
    id: int
    status: RoomStatus
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
    room_id: int
    room_no: str
    badge_text: Union[BadgeTexts, RoomStatus]
    badge_variant: BadgeVariants
    main_display_text: str
    sub_display_text: str
    is_owing: bool = False


if __name__ == '__main__':

    summary_dict = {
        'lease_id': 1,
        'room_no': '29',
        'badge_text': BadgeTexts.SAFE,
        'badge_variant': BadgeVariants.SUCCESS,
        'main_display_text': 'Donald',
        'sub_display_text': '91 days left'
    }

    print(RoomGridSummary.model_validate(summary_dict).model_dump_json(indent=4))

