from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import user as schema_user
from app.crud import user as crud_user
from app.core.enums import UserRole
from .exceptions import UserAlreadyExistError

def _sign_up_user(
        user_data: schema_user.UserCreate,
        db: Session,
        role: UserRole = UserRole.LANDLORD
):
    user_exist = crud_user.get_user_by_email(db=db, email=user_data.email.lower())

    if user_exist:
        raise UserAlreadyExistError(email=user_exist.email)

    return crud_user.create_user(db=db, user_data=user_data, role=role)
