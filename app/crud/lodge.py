from sqlalchemy import or_, literal, func, select, and_, RowMapping, case, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import cast

from app.core.enums import RoomStatus, BadgeTexts, LeaseStatus
from app.crud.payment import crud_payment
from app.models.lease import Lease
from app.models.lodge import Lodge
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.schemas.entity_count import EntityCountResponse, OccupiedCounts
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.crud.base_crud import CRUDBase
from app.schemas.room import RoomStatusCounts


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

    def get_room_status_counts(self, db: Session, lodge_id: int):
        occupied_expr = func.count(case((Room.status == RoomStatus.OCCUPIED, 1), else_=None))

        vacant_expr = func.count(case((Room.status == RoomStatus.VACANT, 1), else_=None))

        maintenance_expr = func.count(case((Room.status == RoomStatus.MAINTENANCE, 1), else_=None))

        stmt = select(
            occupied_expr.label('occupied'),
            vacant_expr.label('vacant'),
            maintenance_expr.label('maintenance')
        ).where(
            Room.lodge_id == lodge_id
        )

        result = db.execute(stmt).mappings().first()

        return result

    def get_tenant_counts(self, db: Session, lodge_id: int):
        tenant_count_expr = func.count(TenantProfile.id)
        stmt = select(tenant_count_expr.label('total_tenants')).where(TenantProfile.lodge_id == lodge_id)

        result = db.execute(stmt).mappings().first()
        return result

    def get_occupied_counts(self, db: Session, lodge_id: int):
        payment_subq = crud_payment.get_payment_subq()
        days_left = cast(func.julianday(Lease.end_date) - func.julianday('now'), Integer) #only supported by sqlite,
        #change in production to postgres

        total_paid = func.coalesce(payment_subq.c.total_amt_paid, 0)
        incomplete_payment = total_paid < Lease.agreed_rent_amt

        owing_expr = func.count(
            case(
                (and_(Room.status == RoomStatus.OCCUPIED, incomplete_payment), 1), else_=None
            )
        )

        has_payed = total_paid == Lease.agreed_rent_amt

        safe_expr = func.count(
            case(
                (and_(days_left >= 90, has_payed), 1), else_=None
            )
        )

        expiring_expr = func.count(
            case(
                (and_(days_left.between(0, 89), has_payed), 1), else_=None
            )
        )

        overdue_expr = func.count(
            case(
                (and_(days_left < 0, has_payed), 1), else_=None
            )
        )



        stmt = select(
            safe_expr.label('safe'),
            expiring_expr.label('expiring'),
            overdue_expr.label('overdue'),
            owing_expr.label('owing')
        ).select_from(Lease).outerjoin(
            Room, Lease.room_id == Room.id
        ).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id,
            Lease.status == LeaseStatus.ACTIVE,
            Room.status == RoomStatus.OCCUPIED
        )

        result = db.execute(stmt).mappings().first()
        return result




crud_lodge = CRUDLodge(Lodge)
