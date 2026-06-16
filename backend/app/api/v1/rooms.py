"""
API routes for managing rooms.

Provides endpoints for landlords to create, retrieve, and update rooms within their lodges.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.crud.room import crud_room
from app.schemas import room as schema_room
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_landlord_user
from app.models.user import User
from app.services import room_service

router = APIRouter()


@router.get('/', response_model=List[schema_room.RoomResponse])
def get_landlord_rooms(
        skip: Optional[int] = None,
        limit:  Optional[int] = None,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    """
    Retrieve all rooms for lodges owned by the authenticated landlord.

    Args:
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        db (Session): The database session.
        landlord_user (User): The authenticated landlord user.

    Returns:
        List[schema_room.RoomResponse]: A list of rooms.
    """
    return room_service.get_lodge_rooms(
        db,
        landlord_id=landlord_user.id,
        skip=skip,
        limit=limit
    )


@router.post('/', response_model=schema_room.RoomResponse)
def create_room(
        room_in: schema_room.RoomCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    """
    Create a new room in a specific lodge owned by the landlord.

    Args:
        room_in (schema_room.RoomCreate): The room data to create.
        db (Session): The database session.
        landlord_user (User): The authenticated landlord user.

    Returns:
        schema_room.RoomResponse: The created room.
    """
    return room_service.create_room_for_lodge(
        db=db, room_in=room_in,
        landlord_id=landlord_user.id
    )


@router.get('/{room_id}', response_model=schema_room.RoomResponse)
def get_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a specific room by its ID.

    Args:
        room_id (int): The ID of the room.
        db (Session): The database session.
        current_user (User): The authenticated user.

    Returns:
        schema_room.RoomResponse: The retrieved room.
    """
    room = room_service.get_room_details(db, landlord_id=current_user.id, room_id=room_id)
    return room


@router.patch('/{room_id}', response_model=schema_room.RoomResponse)
def update_room_by_id(
        room_id: int,
        update_data: schema_room.RoomUpdate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    """
    Update details of a specific room.

    Args:
        room_id (int): The ID of the room to update.
        update_data (schema_room.RoomUpdate): The updated room data.
        db (Session): The database session.
        landlord_user (User): The authenticated landlord user.

    Returns:
        schema_room.RoomResponse: The updated room.
    """
    updated_room = room_service.update_room_details(
        db, room_id=room_id,
        update_data=update_data,
        landlord_id=landlord_user.id
    )
    return updated_room
