from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from app.crud import room as crud_room
from app.schemas import room as schema_room
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import LandLord
router = APIRouter()



@router.get('/', response_model=List[schema_room.RoomResponse])
def get_all_rooms(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user: LandLord = Depends(get_current_user)
):
    return crud_room.get_rooms(db=db,skip=skip, max_limit=limit)


@router.post('/create-room', response_model=schema_room.RoomResponse)
def create_room(
        room_in: schema_room.RoomCreate,
        db: Session = Depends(get_db),
        current_user: LandLord = Depends(get_current_user)
):
    room = crud_room.get_room_by_number(db=db, room_no=room_in.room_no)

    if room:
        raise HTTPException(
            status_code=400,
            detail=f'Room {room_in.room_no} already exists'
        )
    return crud_room.create_room(db=db, room_data=room_in)


@router.get('/{room_id}', response_model=schema_room.RoomResponse)
def get_room(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: LandLord = Depends(get_current_user)
):
    room = crud_room.get_room(db=db, room_id=room_id)

    if not room:
        raise HTTPException(
            status_code=404,
            detail=f'Room not found'
        )
    return room


@router.patch('/', response_model=schema_room.RoomResponse)
def update_room_by_room_no(
        room_no: str,
        update_data: schema_room.RoomUpdate,
        db: Session = Depends(get_db),
        current_user: LandLord = Depends(get_current_user)
):
    room = crud_room.get_room_by_number(db=db, room_no=room_no)

    if not room:
        raise HTTPException(
            status_code=404,
            detail='Room not found'
        )
    return crud_room.update_room(db=db, room_data=update_data, db_room=room)





