from app.schemas import room as schema_room
from app.crud import room as crud_room
from sqlalchemy.orm import Session
from app.services import lodge_service
from app.services.exceptions import RoomNotFoundError, RoomAlreadyExistError


#check if lodge exist -> proceed
#check if room exist -> error
#
def create_room_for_lodge(db:Session,  room_in: schema_room.RoomCreate, lodge_id: int, landlord_id: int):
    lodge_service.get_lodge_for_landlord(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    room = crud_room.get_room_by_lodge_and_number(db=db, room_no=room_in.room_no, lodge_id=lodge_id)

    if room:
        print('room exists, waiting to check if room exist in lodge')
        raise RoomAlreadyExistError(room_in.room_no)

    return crud_room.create_room(db=db, room_data=room_in, lodge_id=lodge_id)


def get_lodge_rooms():
    pass


def get_room_details():
    pass


def update_room_details():
    pass


