from typing import Unpack

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.generic_extras import GenericExtras

from app.crud.base_crud import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_user_by_email(self, db: Session, email: str):
        print(f'User input email: {email}')
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate, **kwargs: Unpack[GenericExtras]) -> User:
        obj_data = obj_in.model_dump()

        password = obj_data.pop('password')
        obj_data['hashed_password'] = get_password_hash(password=password)

        db_user = User(**obj_data, **kwargs)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


crud_user = CRUDUser(User)
