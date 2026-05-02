from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import user as schema_user
from app.crud.user import crud_user
from app.core.enums import UserRole
from .exceptions import UserAlreadyExistError
from app.core.security import verify_password_hash


def sign_up_user(
        user_data: schema_user.UserCreate,
        db: Session,
        role: UserRole = UserRole.LANDLORD
):
    user = crud_user.get_user_by_email(db=db, email=user_data.email)

    if user:
        raise UserAlreadyExistError(email=user.email)

    return crud_user.create(db=db, obj_in=user_data, role=role)


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by checking their email and password.
    """
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password_hash(password, user.hashed_password):
        return None
    return user
