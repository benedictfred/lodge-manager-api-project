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




crud_user = CRUDUser(User)
