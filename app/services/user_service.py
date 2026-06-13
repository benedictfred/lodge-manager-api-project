from sqlalchemy.orm import Session

from app.crud.user import crud_user
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError, UnauthorizedAccessError
from app.core.security import verify_password_hash, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserInternal


def sign_up_landlord(
        db: Session,
        landlord_data: UserCreate,
)-> User:
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
    authenticated_user = authenticate_user(db, email=email, password=password)

    if not authenticated_user:
        raise UnauthorizedAccessError()

    access_token = create_access_token(
        subject=str(authenticated_user.id)
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }
