from sqlalchemy import or_, literal, func, select, and_, case
from sqlalchemy.orm import Session
from app.core.enums import RoomStatus, LeaseStatus, BadgeTexts
from app.models.lease import Lease
from app.models.lodge import Lodge
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.crud.base_crud import CRUDBase
from app.core import constants as const


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
        occupied_count_expr = func.count(case((const.occupied_expr, 1), else_=None))

        vacant_count_expr = func.count(case((const.vacant_expr, 1), else_=None))

        maintenance_count_expr = func.count(case((const.maintenance_expr, 1), else_=None))

        stmt = select(
            occupied_count_expr.label('occupied'),
            vacant_count_expr.label('vacant'),
            maintenance_count_expr.label('maintenance')
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


        owing_count_expr = func.count(
            case(
                (and_(*const.filter_menu.get(BadgeTexts.OWING)), 1), else_=None
            )
        )


        safe_count_expr = func.count(
            case(
                (and_(*const.filter_menu.get(BadgeTexts.SAFE)), 1), else_=None
            )
        )

        expiring_count_expr = func.count(
            case(
                (and_(*const.filter_menu.get(BadgeTexts.EXPIRING)), 1), else_=None
            )
        )

        overdue_expr = func.count(
            case(
                (and_(*const.filter_menu.get(BadgeTexts.OVERDUE)), 1), else_=None
            )
        )

        stmt = select(
            safe_count_expr.label('safe'),
            expiring_count_expr.label('expiring'),
            overdue_expr.label('overdue'),
            owing_count_expr.label('owing')
        ).select_from(Lease).outerjoin(
            Room, Lease.room_id == Room.id
        ).outerjoin(
            const.payment_subq, const.payment_subq.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id,
            Lease.status == LeaseStatus.ACTIVE,
            Room.status == RoomStatus.OCCUPIED
        )

        result = db.execute(stmt).mappings().first()
        return result




crud_lodge = CRUDLodge(Lodge)
