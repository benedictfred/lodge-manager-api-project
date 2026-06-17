from app.core.config import settings
from passlib.context import CryptContext
import jwt
from typing import Union, Any

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
from datetime import timedelta, datetime, timezone


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



def verify_password_hash(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        subject: Union[str, Any],
        expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        'sub': str(subject),
        'exp': expires,
        'type': 'access'
    }

    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(subject: Union[str, Any],
                         expires_delta: timedelta = None) -> str:
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode =  {
        'sub': subject,
        'exp': expires,
        'type': 'refresh'
    }

    encoded_refresh_token = jwt.encode(
        to_encode,
        algorithm=settings.ALGORITHM,
        key=settings.REFRESH_SECRET_KEY
    )
    return encoded_refresh_token