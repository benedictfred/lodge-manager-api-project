from sqlalchemy import or_, literal, func, select, and_
from sqlalchemy.orm import Session

from app.core.enums import RoomStatus
from app.crud.payment import crud_payment
from app.models.lease import Lease
from app.models.lodge import Lodge
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.schemas.entity_count import EntityCountResponse
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
    def get_lodges_by_owner(self, db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id
        ).offset(skip).limit(limit).all()

    def get_all_entities_count(self, db: Session, lodge_id: int):
        payment_subq = crud_payment.get_payment_subq()

        days_left = Lease.end_date - func.current_date()
        has_payed = func.sum(payment_subq.c.total_paid) == Lease.agreed_rent_amt
        not_payed = func.sum(payment_subq.c.total_paid) < Lease.agreed_rent_amt

        SAFE_DAYS = 90
        EXPIRING_DAYS_START = 30
        EXPIRING_DAYS_END = 0


        room_count_scalar_subq = select(func.count(Room.id)).scalar_subquery()
        tenant_count_scalar_subq = select(func.count(TenantProfile.id).label('tenant_count')).scalar_subquery()
        vacant_count_scalar_subq = select(func.count(Room.status == RoomStatus.VACANT).label('vacant')).scalar_subquery()
        maintenance_count_scalar_subq = select(func.count(Room.status == RoomStatus.MAINTENANCE).label('maintenance')).scalar_subquery()
        occupied_count_scalar_subq = select(func.count(Room.status == RoomStatus.OCCUPIED).label('occupied')).scalar_subquery()
        safe_count_scalar_subq = select(func.count(
            and_(Room.status == RoomStatus.OCCUPIED, days_left >= SAFE_DAYS, has_payed)
        ).label('safe')).scalar_subquery()

        expiring_count_scalar_subq = select(func.count(
            and_(Room.status == RoomStatus.OCCUPIED, days_left <= EXPIRING_DAYS_START, days_left >= EXPIRING_DAYS_END,
                 has_payed)
        ).label('expiring')).scalar_subquery()

        overdue_count_scalar_subq = select(func.count(
            and_(Room.status == RoomStatus.OCCUPIED, days_left < EXPIRING_DAYS_END, has_payed)
        ).label('overdue')).scalar_subquery()

        owing_count_scalar_subq = select(func.count(
            and_(Room.status == RoomStatus.OCCUPIED, not_payed)
        ).label('owing')).scalar_subquery()

        stmt = select(
            room_count_scalar_subq.label('room_count'),
            tenant_count_scalar_subq,
            vacant_count_scalar_subq,
            maintenance_count_scalar_subq,
            occupied_count_scalar_subq,
            safe_count_scalar_subq,
            expiring_count_scalar_subq,
            overdue_count_scalar_subq,
            owing_count_scalar_subq,
        ).where(
            Room.lodge_id == lodge_id
        ).group_by(
            Lease.end_date,
            Lease.agreed_rent_amt,
            Room.id,
            TenantProfile.id,
            Room.status,
        )

        db_entity_count =   db.execute(stmt).mappings().first()
        return  EntityCountResponse(**db_entity_count) if db_entity_count else None



crud_lodge = CRUDLodge(Lodge)
