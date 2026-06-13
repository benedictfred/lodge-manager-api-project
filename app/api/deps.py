import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotLandlordError, NotTenantError, UserNotFoundError
from app.db.session import SessionLocal
from typing import Generator
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.crud.user import crud_user
from app.models.user import User
from app.services.lodge_service import is_landlord, is_tenant

#helps to extract token from http request
oauth_2 = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login'
)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth_2)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Could not validate credentials'
    )
    try:

        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]

        )
        user_id = payload.get('sub')
        if not user_id:
            raise credentials_exception
    except (jwt.PyJWTError, ValueError, ValidationError):
        raise credentials_exception

    user = crud_user.get(db=db, item_id=user_id)

    if not user:
        raise UserNotFoundError()

    return user


#dependency for ensuring the user is a landlord
#get the current logged in user(validated and authenticated)
#check if the user object is of the role of landlord -> allow the user to the route that needs the dependency

def get_landlord_user(
        current_user: User = Depends(get_current_user)
):
    if not is_landlord(current_user.role):
       raise NotLandlordError()
    return current_user


def get_tenant_user(
        current_user: User = Depends(get_current_user)
):
    if not is_tenant(current_user.role):
        raise NotTenantError()
    return current_user