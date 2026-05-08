
from app.models.room import  Room
from app.schemas.room import RoomCreate, RoomUpdate
from sqlalchemy.orm import Session
from app.crud.base_crud import CRUDBase
from sqlalchemy import or_, literal


class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    #method to get room by lodge and number
    # method to get many rooms in a lodge with pagination support

    def get_room_by_lodge_and_number(self, db: Session, room_no: str, lodge_id: int):
        """Retrieve a specific room by its room number."""

        return db.query(self.model).filter(
            self.model.lodge_id == lodge_id,
            self.model.room_no == room_no
        ).first()


    def get_rooms(self, db: Session, lodge_id: int, skip: int = 0, max_limit: int = 50):
        """Retrieve a list of rooms with pagination support."""
        return db.query(self.model).filter(self.model.lodge_id == lodge_id).offset(skip).limit(max_limit).all()



crud_room= CRUDRoom(Room)


