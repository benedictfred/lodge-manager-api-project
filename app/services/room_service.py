from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session
from app.services import lodge_service
from app.core.exceptions import RoomAlreadyExistError, LodgeNotFoundError, RoomNotFoundError


def create_room_for_lodge(db: Session, room_in: schema_room.RoomCreate, lodge_id: int, landlord_id: int):
    lodge_service.verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    room = crud_room.get_room_by_lodge_and_number(db=db, room_no=room_in.room_no, lodge_id=lodge_id)

    if room:
        print('room exists, waiting to check if room exist in lodge')
        raise RoomAlreadyExistError(room_in.room_no)

    return crud_room.create(db=db, obj_in=room_in, lodge_id=lodge_id)


def get_lodge_rooms(db: Session, lodge_id: int, landlord_id, skip: int, limit: int):
    lodge_service.verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    return crud_room.get_rooms(db, lodge_id=lodge_id, skip=skip, max_limit=limit)


def verify_room_existence(db: Session, lodge_id: int, room_id: int):
    room = crud_room.get(db, item_id=room_id)
    room_exist_in_lodge = room.lodge_id != lodge_id

    if not room or room_exist_in_lodge:
        raise RoomNotFoundError()

    return room


def get_room_details(db: Session, lodge_id: int, room_id: int, landlord_id: int):
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    room = verify_room_existence(db, room_id=room_id, lodge_id=lodge.id)
    return room


def update_room_details(db: Session, lodge_id: int, landlord_id: int, room_id: int, update_data: schema_room.RoomUpdate):
    #verify that lodge exist ->
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    #verify that the room exists ->
    #verify that room exists in lodge
    room = verify_room_existence(db, lodge_id=lodge.id, room_id=room_id)

    updated_room =  crud_room.update(db, db_obj=room, update_data=update_data)
    return updated_room
