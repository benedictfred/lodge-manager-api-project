from typing import Union
from app.models.room import  Room
from app.schemas.room import RoomCreate, RoomUpdate
from sqlalchemy.orm import Session


def get_room_by_number(db: Session, room_no: str):
    """Retrieve a specific room by its room number."""
    return db.query(Room).filter(Room.room_no == room_no).first()


def create_room(db: Session, room_data: RoomCreate):
    """Create a new room record in the database."""
    # Convert the Pydantic schema to a dictionary and unpack into the SQLAlchemy model
    db_room = Room(**room_data.model_dump())

    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    return db_room


def update_room(db: Session, room_data: RoomUpdate, db_room: Room):
    """Update an existing room found by its primary key ID."""
    # Only extract fields that were actually provided in the update request
    update_data = room_data.model_dump(exclude_unset=True)

    # Update the model attributes dynamically
    for key, value in update_data.items():
        setattr(db_room, key, value)

    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def get_room(db: Session, room_id: int, lodge_id: int):
    """Retrieve a specific room by its primary key ID."""
    return db.query(Room).filter(Room.id == room_id, Room.lodge_id == lodge_id).first()


def get_rooms(db: Session, lodge_id: int, skip: int = 0, max_limit: int = 50):
    """Retrieve a list of rooms with pagination support."""
    return db.query(Room).filter(Room.lodge_id == lodge_id).offset(skip).limit(max_limit).all()