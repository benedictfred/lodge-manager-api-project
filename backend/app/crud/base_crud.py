"""
Module providing base CRUD operations.

This module contains a generic base class for Create, Read, Update, and Delete
(CRUD) operations using SQLAlchemy.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Generic, Type, TypeVar, Unpack, List, Optional
from pydantic import BaseModel

from app.schemas.generic_extras import GenericExtras

ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)



class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.
    """
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the base CRUD class.

        Args:
            model (Type[ModelType]): The SQLAlchemy model class.
        """
        self.model = model

    def get(self, db: Session, item_id: int,  *options) -> Optional[ModelType]:
        """
        Get a single record by its ID.

        Args:
            db (Session): The database session.
            item_id (int): The ID of the item to retrieve.

        Returns:
            Optional[ModelType]: The retrieved item or None if not found.
        """
        stmt = select(self.model).where(self.model.id == item_id)

        if options:
            stmt = stmt.options(*options)

        return db.execute(stmt).scalar_one_or_none()

    def get_multi(self, db: Session, item_id: int, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db (Session): The database session.
            item_id (int): The ID to filter by.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            List[ModelType]: A list of retrieved records.
        """
        return db.query(self.model).filter(self.model.id == item_id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType, **kwargs: Unpack[GenericExtras]):
        """
        Create a new record in the database.

        Args:
            db (Session): The database session.
            obj_in (CreateSchemaType): The schema containing data to create the record.
            **kwargs (Unpack[GenericExtras]): Additional generic extra parameters.

        Returns:
            ModelType: The newly created database object.
        """
        db_object = self.model(**obj_in.model_dump(), **kwargs)
        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def update(self, db: Session, update_data: UpdateSchemaType, db_obj: ModelType) -> ModelType:
        """
        Update an existing database record.

        Args:
            db (Session): The database session.
            update_data (UpdateSchemaType): The schema containing updated data.
            db_obj (ModelType): The database object to be updated.

        Returns:
            ModelType: The updated database object.
        """
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(db_obj, key, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ModelType):
        """
        Delete a record from the database.

        Args:
            db (Session): The database session.
            db_obj (ModelType): The database object to delete.

        Returns:
            None
        """
        db.delete(db_obj)
        db.commit()




