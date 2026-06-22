"""
Module providing room-related business logic.

This module contains services for managing rooms.
"""
from sys import prefix
from typing import Optional

from app.core import constants
from app.core.enums import RoomStatus
from app.models.room import Room
from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session, joinedload

from app.schemas.lodge import LodgeCreate
from app.schemas.room import RoomResponse, RoomCreate, BulkRoomUpdate
from app.services import lodge_service
from app.core.exceptions import RoomAlreadyExistError, RoomNotFoundError, RoomIsOccupiedError, NotUpdatableOptionError



def create_room_for_lodge(db: Session, room_in: schema_room.RoomCreate, landlord_id: int) -> Room:
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



def get_lodge_rooms(db: Session,
                    lodge_id:int,
                    landlord_id: int,
                    skip: Optional[int] = None,
                    limit: Optional[int] = None
                    ):
    """
    Get all rooms for a specific landlord's lodges.

    Args:
        lodge_id:
        db (Session): The database session.
        landlord_id (int): The ID of the landlord.
        skip (Optional[int]): Number of records to skip. Defaults to None.
        limit (Optional[int]): Maximum number of records to return. Defaults to None.

    Returns:
        List[Room]: A list of rooms.
    """
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    return crud_room.get_rooms(db, landlord_id=landlord_id, lodge_id= lodge_id, skip=skip, max_limit=limit)


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
    options = joinedload(Room.lodge)
    room = crud_room.get(db, room_id, options)

    if not room or not lodge_service.landlord_owns_room_lodge(room=room, landlord_id=landlord_id):
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
        raise RoomIsOccupiedError(occupied_room_no=room.room_no)

    if update_data.status and update_data.status not in constants.UPDATABLE_ROOM_STATUSES:
        raise NotUpdatableOptionError(allowed_options=constants.UPDATABLE_ROOM_STATUSES,
                                      update_status=update_data.status)

    return crud_room.update(db, db_obj=room, update_data=update_data)

def bulk_update_base_rent(
        db: Session,
        lodge_id: int,
        update_data: BulkRoomUpdate,
        landlord_id: int
):
    from app.services.lodge_service import verify_lodge_ownership

    verify_lodge_ownership(db, lodge_id, landlord_id)

    to_update_rooms = crud_room.get_updatable_rooms(
        db,
        room_ids= update_data.room_ids,
        lodge_id=lodge_id
    )

    if not to_update_rooms:
        room_nos_str = ', '.join(str(n) for n in update_data.room_ids)
        raise RoomNotFoundError(room_nos_str)

    if len(to_update_rooms) != len(update_data.room_ids):

        raise RoomNotFoundError(detail='One or more rooms')

    for room in to_update_rooms:
        if room.status  == RoomStatus.OCCUPIED:
            raise RoomIsOccupiedError(occupied_room_no=room.room_no)

        room.base_rent_price = update_data.base_rent

    db.commit()

    return to_update_rooms



