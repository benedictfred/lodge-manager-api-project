import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import  SessionLocal
from typing import Generator
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.crud.user import crud_user


#helps to extract token from http request
oauth_2 = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login'
)

def get_db() -> Generator :
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
        db: Session  = Depends(get_db),
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

    user = crud_user.get(db=db,item_id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    return user