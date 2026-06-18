"""
Module providing room-related business logic.

This module contains services for managing rooms.
"""
from typing import Optional

from app.core.enums import RoomStatus
from app.models.room import Room
from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session

from app.schemas.room import RoomResponse
from app.services import lodge_service
from app.core.exceptions import RoomAlreadyExistError, RoomNotFoundError, RoomIsOccupiedError


def create_room_for_lodge(db: Session, room_in: schema_room.RoomCreate, landlord_id: int) -> RoomResponse:
    """
    Create a new room in a specific lodge for a landlord.

    Args:
        db (Session): The database session.
        room_in (RoomCreate): The data to create the room.
        landlord_id (int): The ID of the landlord.

    Returns:
        RoomResponse: The newly created room.
    """
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=room_in.lodge_id, landlord_id=landlord_id)

    room = crud_room.get_room_by_lodge_and_number(db=db, room_no=room_in.room_no, lodge_id=lodge.id)

    if room:
        raise RoomAlreadyExistError(room_in.room_no)

    return crud_room.create(db=db, obj_in=room_in)


def get_lodge_rooms(db: Session, landlord_id, skip: Optional[int] = None, limit: Optional[int] = None):
    """
    Get all rooms for a specific landlord's lodges.

    Args:
        db (Session): The database session.
        landlord_id (int): The ID of the landlord.
        skip (Optional[int]): Number of records to skip. Defaults to None.
        limit (Optional[int]): Maximum number of records to return. Defaults to None.

    Returns:
        List[Room]: A list of rooms.
    """
    return crud_room.get_rooms(db, skip=skip, max_limit=limit)


def verify_room_existence(db: Session, landlord_id: int, room_id: int):
    """
    Verify if a room exists and belongs to the landlord.

    Args:
        db (Session): The database session.
        landlord_id (int): The ID of the landlord.
        room_id (int): The ID of the room.

    Returns:
        Room: The verified room.
    """
    room = crud_room.get(db, item_id=room_id)

    if not room or room.lodge.landlord_id != landlord_id:
        raise RoomNotFoundError()

    return room


def get_room_details(db: Session, room_id: int, landlord_id: int):
    """
    Get the details of a specific room.

    Args:
        db (Session): The database session.
        room_id (int): The ID of the room.
        landlord_id (int): The ID of the landlord.

    Returns:
        Room: The requested room details.
    """
    return verify_room_existence(db, room_id=room_id, landlord_id=landlord_id)



def update_room_details(db: Session, room_id: int, landlord_id: int, update_data: schema_room.RoomUpdate):
    """
    Update the details of a specific room.

    Args:
        db (Session): The database session.
        room_id (int): The ID of the room.
        landlord_id (int): The ID of the landlord.
        update_data (RoomUpdate): The data to update.

    Returns:
        Room: The updated room.
    """
    room = verify_room_existence(db, landlord_id=landlord_id, room_id=room_id)

    if room.status == RoomStatus.OCCUPIED:
        raise RoomIsOccupiedError()

    return crud_room.update(db, db_obj=room, update_data=update_data)


