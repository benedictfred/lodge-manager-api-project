from pydantic import BaseModel, ConfigDict

from app.schemas.room import RoomStatusCount


class EntityCountResponse(BaseModel):
    total_rooms: int
    total_tenants: int
    room_status_counts : RoomStatusCount

    model_config = ConfigDict(from_attributes=True)