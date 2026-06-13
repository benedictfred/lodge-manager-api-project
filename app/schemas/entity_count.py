from pydantic import BaseModel, ConfigDict, ValidationError

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


if __name__ == "__main__":
    mock_entity_count_dict = {
        'total_rooms': 40,
        'total_tenants': 35,
        'room_status_counts': {
            'occupied': 30,
            'vacant': 6,
            'maintenance':   4
        },
        'occupied_counts': {
            'safe': 10,
            'expiring': 10,
            'overdue': 2,
            'owing': 8
        }
    }
    try:
        mock_entity_count_schema = EntityCountResponse(**mock_entity_count_dict)
        print(mock_entity_count_schema.model_dump_json(indent=4))

    except ValidationError as e:
        raise e
