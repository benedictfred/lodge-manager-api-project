from sqlalchemy import or_, literal
from sqlalchemy.orm import Session
from app.models.lodge import Lodge
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.crud.base_crud import CRUDBase


class CRUDLodge(CRUDBase[Lodge, LodgeCreate, LodgeUpdate]):
    #method for getting lodge owned by a specific landlord
    def get_by_landlord(self, db: Session, landlord_id: int, lodge_id: int):
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id, self.model.id == lodge_id
        ).first()

    #method to getting lodge owned by a specific landlord with a specific lodge name
    def get_by_name_and_landlord(self, db: Session, landlord_id: int, lodge_name: str):
        search = f'%{lodge_name}%'
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id,
            or_(
                self.model.name.ilike(search),
                literal(search).ilike(self.model.name.concat('%'))
            )
        ).first()

    #method to get lodges owned by a specific landlord
    def get_multi_by_owner(self, db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id
        ).offset(skip).limit(limit).all()


crud_lodge = CRUDLodge(Lodge)
