from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.core.exceptions import LodgeAlreadyExistError, LodgeNotFoundError
from app.crud.lodge import crud_lodge

def is_landlord(user_role: UserRole):
    return user_role == UserRole.LANDLORD


def create_new_loge_for_landlord(db: Session, landlord_id: int, lodge_in: LodgeCreate):
    lodge_exist = crud_lodge.get_by_name_and_landlord(db, landlord_id=landlord_id, lodge_name=lodge_in.name)

    if lodge_exist:
        raise LodgeAlreadyExistError(name=lodge_in.name)

    return crud_lodge.create(db, obj_in=lodge_in, landlord_id=landlord_id)

def verify_lodge_ownership(db: Session, lodge_id:int, landlord_id: int):
    lodge = crud_lodge.get(db, item_id=lodge_id)

    if not lodge:
        raise LodgeNotFoundError()

    owned_by_landlord = lodge.landlord_id == landlord_id

    if not owned_by_landlord:
        raise LodgeNotFoundError()

    return lodge


def update_landlord_lodge(db:Session, lodge_id: int, landlord_id: int, update_data: LodgeUpdate):
    lodge = verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_id)

    return crud_lodge.update(db=db, update_data=update_data, db_lodge=lodge)

