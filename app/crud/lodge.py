from sqlalchemy.orm import Session
from app.models.lodge import Lodge
from app.schemas.lodge import LodgeCreate, LodgeUpdate


# crud_lodge.py
def create_lodge(db: Session, lodge_data: LodgeCreate, landlord_id: int):
    # The CRUD layer just takes the raw integer and builds the row
    db_lodge = Lodge(**lodge_data.model_dump())
    db_lodge.landlord_id = landlord_id

    db.add(db_lodge)
    db.commit()
    db.refresh(db_lodge)
    return db_lodge


def get_lodge_by_name_and_landlord(db: Session, landlord_id: int, lodge_name: str):
    return db.query(Lodge).filter(Lodge.landlord_id == landlord_id, Lodge.name == lodge_name).first()



def get_lodges(db: Session, landlord_id: int, skip: int= 0, limit: int =50):
    return db.query(Lodge).filter(Lodge.landlord_id == landlord_id).offset(skip).limit(limit).all()


def get_lodge(db:Session, landlord_id: int , lodge_id):
    return db.query(Lodge).filter(Lodge.landlord_id == landlord_id, Lodge.id == lodge_id).first()



def update_lodge(db: Session, db_lodge: Lodge, lodge_data: LodgeUpdate):

    # Only extract fields that were actually provided in the update request
    update_data = lodge_data.model_dump(exclude_unset=True)

    # Update the model attributes dynamically
    for key, value in update_data.items():
        setattr(db_lodge, key, value)

    db.add(db_lodge)
    db.commit()
    db.refresh(db_lodge)
    return db_lodge