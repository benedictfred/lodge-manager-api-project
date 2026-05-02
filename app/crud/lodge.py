from sqlalchemy.orm import Session
from app.models.lodge import Lodge
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.crud.base_crud import CRUDBase


class CRUDLodge(CRUDBase[Lodge, LodgeCreate, LodgeUpdate]):
    #method for getting lodge owned by a specific landlord
    def get_lodge_by_landlord(self, db: Session, landlord_id: int, lodge_id: int):
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id, self.model.id == lodge_id).first()

    #method to getting lodge owned by a specific landlord with a specific lodge name
    def get_lodge_by_name_and_landlord(self, db: Session, landlord_id: int, lodge_name: str):
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id, self.model.name == lodge_name).first()



crud_lodge = CRUDLodge(Lodge)

