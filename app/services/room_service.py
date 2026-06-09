from typing import Optional

from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session

from app.schemas.room import RoomResponse
from app.services import lodge_service
from app.core.exceptions import RoomAlreadyExistError, RoomNotFoundError


def create_room_for_lodge(db: Session, room_in: schema_room.RoomCreate, landlord_id: int) -> RoomResponse:
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=room_in.lodge_id, landlord_id=landlord_id)

    room = crud_room.get_room_by_lodge_and_number(db=db, room_no=room_in.room_no, lodge_id=lodge.id)

    if room:
        raise RoomAlreadyExistError(room_in.room_no)

    return crud_room.create(db=db, obj_in=room_in)


def get_lodge_rooms(db: Session, landlord_id, skip: Optional[int] = None, limit: Optional[int] = None):
    return crud_room.get_rooms(db, skip=skip, max_limit=limit)


def verify_room_existence(db: Session, landlord_id: int, room_id: int):
    room = crud_room.get(db, item_id=room_id)

    if not room or room.lodge.landlord_id != landlord_id:
        raise RoomNotFoundError()

    return room


def get_room_details(db: Session, room_id: int, landlord_id: int):
    return verify_room_existence(db, room_id=room_id, landlord_id=landlord_id)



def update_room_details(db: Session, room_id: int, landlord_id: int, update_data: schema_room.RoomUpdate):
    room = verify_room_existence(db, landlord_id=landlord_id, room_id=room_id)

    return crud_room.update(db, db_obj=room, update_data=update_data)


