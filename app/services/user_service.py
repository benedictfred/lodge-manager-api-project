from sqlalchemy.orm import Session

from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError
from app.core.security import verify_password_hash, get_password_hash
from app.schemas.tenantprofile import TenantProfileCreate
from app.schemas.user import UserCreate, UserInternal


def sign_up_landlord(
        db: Session,
        landlord_data: UserCreate,
):
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
        return None
    if not verify_password_hash(password, user.hashed_password):
        return None
    return user
