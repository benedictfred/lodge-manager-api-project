from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.enums import UserRole

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()


def create_user(db: Session, user_data: UserCreate, role: UserRole) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email.lower(),
        hashed_password=hashed_password,
        role=role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


