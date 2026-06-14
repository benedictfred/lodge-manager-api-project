"""
Module providing user-related CRUD operations.

This module contains the CRUD operations for User models, inheriting from
the base CRUD functionality.
"""
from typing import Unpack

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInternal
from app.schemas.generic_extras import GenericExtras

from app.crud.base_crud import CRUDBase, CreateSchemaType


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD class for User model operations.
    """

    def get_user_by_email(self, db: Session, email: str):
        """
        Get a user by their email address.

        Args:
            db (Session): The database session.
            email (str): The email address to search for.

        Returns:
            User: The found user or None.
        """
        print(f'User input email: {email}')
        return db.query(self.model).filter(self.model.email == email).first()




crud_user = CRUDUser(User)
