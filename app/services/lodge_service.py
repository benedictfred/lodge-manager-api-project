from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.schemas.lodge import LodgeCreate
from app.crud import lodge as crud_lodge
from app.services.exceptions import LodgeAlreadyExistError, LodgeNotFoundError


def is_landlord(user_role: UserRole):
    return user_role == UserRole.LANDLORD


def process_new_lodge(db: Session, landlord_id: int, lodge_in: LodgeCreate):
    lodge_exist = crud_lodge.get_lodge_by_name_and_landlord(db, landlord_id=landlord_id, lodge_name=lodge_in.name)

    if lodge_exist:
        raise LodgeAlreadyExistError(f'Lodge with name: {lodge_in.name} already exists')

    return crud_lodge.create_lodge(db, lodge_data=lodge_in, landlord_id=landlord_id)

def get_lodge_by_id(db: Session, lodge_id:int, landlord_id: int):
    lodge = crud_lodge.get_lodge(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    if not lodge:
        raise LodgeNotFoundError(f'Lodge not found')

    return lodge


def update_lodge_details(db:Session, lodge_id: int, landlord_id: int, update_data):
    lodge = get_lodge_by_id(db=db, lodge_id=lodge_id,landlord_id=landlord_id)

    return crud_lodge.update_lodge(db=db, lodge_data=update_data, db_lodge=lodge)

