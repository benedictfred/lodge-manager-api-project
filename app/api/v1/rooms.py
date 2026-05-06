from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.crud.room import crud_room
from app.schemas import room as schema_room
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_landlord_user
from app.models.user import User
from app.services import room_service
from app.core.exceptions import LodgeNotFoundError, RoomAlreadyExistError, RoomNotFoundError

router = APIRouter()


@router.get('/{lodge_id}/rooms', response_model=List[schema_room.RoomResponse])
def get_all_rooms(
        lodge_id: int,
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    try:
        return room_service.get_lodge_rooms(
            db,
            lodge_id=lodge_id,
            landlord_id=landlord_user.id,
            skip=skip,
            limit=limit
        )
    except LodgeNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post('/{lodge_id}', response_model=schema_room.RoomResponse)
def create_room(
        lodge_id: int,
        room_in: schema_room.RoomCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    try:
        return room_service.create_room_for_lodge(
            db=db, room_in=room_in,
            lodge_id=lodge_id,
            landlord_id=landlord_user.id
        )

    except RoomAlreadyExistError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except LodgeNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.get('/{lodge_id}/rooms/{room_id}', response_model=schema_room.RoomResponse)
def get_room(
        lodge_id: int,
        room_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        room = room_service.get_room_details(db, lodge_id=lodge_id, landlord_id=current_user.id, room_id=room_id)
        return room
    except LodgeNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except RoomNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.patch('/{room_id}', response_model=schema_room.RoomResponse)
def update_room_by_id(

        room_id: int,
        update_data: schema_room.RoomUpdate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    #does the lodge exist and owned by landlord
    #does the room exist and exist in lodge

    try:
        updated_room = room_service.update_room_details(
            db, room_id=room_id,
            update_data=update_data,
        )
        return updated_room
    except RoomNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except LodgeNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
