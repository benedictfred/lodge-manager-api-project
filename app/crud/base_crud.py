from sqlalchemy.orm import Session
from typing import Generic, Type, TypeVar, Unpack, List, Optional
from pydantic import BaseModel

from app.schemas.generic_extras import GenericExtras

ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)



class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, item_id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == item_id).first()

    def get_multi(self, db: Session, item_id: int, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).filter(self.model.id == item_id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType, **kwargs: Unpack[GenericExtras]):
        db_object = self.model(**obj_in.model_dump(), **kwargs)
        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def update(self, db: Session, update_data: UpdateSchemaType, db_obj: ModelType) -> ModelType:
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(db_obj, key, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ModelType):
        db.delete(db_obj)
        db.commit()




