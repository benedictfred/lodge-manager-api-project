from typing import Unpack

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInternal
from app.schemas.generic_extras import GenericExtras

from app.crud.base_crud import CRUDBase, CreateSchemaType


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_user_by_email(self, db: Session, email: str):
        print(f'User input email: {email}')
        return db.query(self.model).filter(self.model.email == email).first()

    def create(self, db: Session, obj_in: UserInternal):
        db_user = User(
            **obj_in.model_dump()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


crud_user = CRUDUser(User)
