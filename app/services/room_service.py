from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session
from app.services import lodge_service
from app.core.exceptions import RoomAlreadyExistError, RoomNotFoundError


def create_room_for_lodge(db: Session, room_in: schema_room.RoomCreate, landlord_id: int):
    lodge = lodge_service.verify_lodge_ownership(db=db, lodge_id=room_in.lodge_id, landlord_id=landlord_id)

    room = crud_room.get_room_by_lodge_and_number(db=db, room_no=room_in.room_no, lodge_id=lodge.id)

    if room:
        raise RoomAlreadyExistError(room_in.room_no)

    return crud_room.create(db=db, obj_in=room_in)


def get_lodge_rooms(db: Session, lodge_id: int, landlord_id, skip: int, limit: int):
    lodge_service.verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    return crud_room.get_rooms(db, lodge_id=lodge_id, skip=skip, max_limit=limit)


def verify_room_existence(db: Session, lodge_id: int, room_id: int):
    room = crud_room.get(db, item_id=room_id)


    if not room or room.lodge_id != lodge_id:
        raise RoomNotFoundError()

    return room


def get_room_details(db: Session, lodge_id: int, room_id: int, landlord_id: int):
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    room = verify_room_existence(db, room_id=room_id, lodge_id=lodge.id)
    return room


def update_room_details(db: Session, room_id: int, landlord_id: int, update_data: schema_room.RoomUpdate):
    room = crud_room.get(db, item_id=room_id)
    if not room:
        raise RoomNotFoundError()

    if room.lodge.landlord_id != landlord_id:
        raise RoomNotFoundError()

    return crud_room.update(db, db_obj=room, update_data=update_data)


