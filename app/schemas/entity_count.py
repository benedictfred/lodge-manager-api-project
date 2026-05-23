from pydantic import BaseModel, ConfigDict

from app.schemas.room import RoomStatusCounts


class EntityCountResponse(BaseModel):
    total_rooms: int
    total_tenants: int
    room_status_counts : RoomStatusCounts
    occupied_counts: OccupiedCounts

    model_config = ConfigDict(from_attributes=True)


class OccupiedCounts(BaseModel):
    safe: int
    expiring: int
    overdue: int
    owing: int
