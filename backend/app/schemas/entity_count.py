"""
Pydantic schemas for entity counting.

This module contains schemas used to represent the counts of different
entities in the system, such as rooms and tenants.
"""
from pydantic import BaseModel, ConfigDict, ValidationError

from app.schemas.room import RoomStatusCounts


class EntityCountResponse(BaseModel):
    """
    Schema representing the count of various entities in the system.

    Attributes:
        total_rooms (int): The total number of rooms.
        total_tenants (int): The total number of tenants.
        room_status_counts (RoomStatusCounts): The counts of rooms by status.
        occupied_counts (OccupiedCounts): The counts of occupied rooms by state.
    """
    total_rooms: int
    total_tenants: int
    room_status_counts : RoomStatusCounts
    occupied_counts: OccupiedCounts

    model_config = ConfigDict(from_attributes=True)


class OccupiedCounts(BaseModel):
    """
    Schema representing the counts of occupied rooms categorized by their lease state.

    Attributes:
        safe (int): Number of rooms with safe leases.
        expiring (int): Number of rooms with expiring leases.
        overdue (int): Number of rooms with overdue payments.
        owing (int): Number of rooms with owing balances.
    """
    safe: int
    expiring: int
    overdue: int
    pending: int
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
