"""
Module providing user-related business logic.

This module contains services for managing users, including authentication.
"""
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import crud_user
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError, UnauthorizedAccessError, UserNotFoundError, \
    InvalidCredentialsError
from app.core.security import verify_password_hash, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate, UserInternal


def sign_up_landlord(
        db: Session,
        landlord_data: UserCreate,
)-> User:
    """
    Sign up a new landlord.

    Args:
        db (Session): The database session.
        landlord_data (UserCreate): The data for the new landlord.

    Returns:
        User: The newly created user.
    """
    user = crud_user.get_user_by_email(db, email=landlord_data.email)

    if user:
        raise UserAlreadyExistError(email=landlord_data.email)

    hashed = get_password_hash(landlord_data.password)

    base_user_data = UserInternal(
        **landlord_data.model_dump(exclude={'password'}),
        hashed_password=hashed,
        role=UserRole.LANDLORD
    )

    return crud_user.create(db, obj_in=base_user_data)


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by checking their email and password.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.
        password (str): The plain text password.

    Returns:
        User: The authenticated user object.
    """
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise UnauthorizedAccessError()

    if not verify_password_hash(password, user.hashed_password):
        raise UnauthorizedAccessError()

    return user


def login_authenticated_user(
        db: Session,
        email: str,
        password: str
):
    """
    Log in an authenticated user and generate an access token.

    Args:
        db (Session): The database session.
        email (str): The email address of the user.
        password (str): The plain text password.

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    authenticated_user = authenticate_user(db, email=email, password=password)

    if not authenticated_user:
        raise UnauthorizedAccessError()

    access_token = create_access_token(
        subject=str(authenticated_user.id)
    )

    refresh_token = create_refresh_token(
        subject=str(authenticated_user.id)
    )


    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


def refresh_access_token(db: Session, refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            key=settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except (jwt.PyJWTError, ValueError, ValidationError):
        raise InvalidCredentialsError()

    if payload.get('type') != 'refresh':
        raise InvalidCredentialsError()

    user_id = payload.get('sub')

    current_user: User = crud_user.get(db=db, item_id=user_id)

    if not current_user or not current_user.is_active:
        raise UserNotFoundError()

    access_token = create_access_token(str(current_user.id))

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }