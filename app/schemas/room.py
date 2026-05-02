from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.models.room import RoomStatus
from datetime import datetime




class RoomBase(BaseModel):
    room_no: str
    description: Optional[str] = None
    base_rent_price: int= Field(default=200000, le=9999999999999)
    status: RoomStatus = RoomStatus.VACANT

    @field_validator('room_no','description')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    lodge_id: int
    created_at: datetime

    model_config = {'from_attributes': True}


class RoomUpdate(BaseModel):
    room_no: Optional[str] = None
    description: Optional[str] = None
    base_rent_price: Optional[int] = None
    status: Optional[RoomStatus] = None


