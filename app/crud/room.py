from app.core.enums import BadgeVariants, LeaseStatus, BadgeTexts, RoomStatus
from app.models.lease import Lease
from app.models.lodge import Lodge
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.dashboard import DashboardFilters
from app.schemas.room import RoomCreate, RoomUpdate
from sqlalchemy.orm import Session
from app.crud.base_crud import CRUDBase
from sqlalchemy import select, case, and_,  func
from app.core import constants as const
from utilities.dashboard_utilities import apply_dashboard_filters


class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    #method to get room by lodge and number
    # method to get many rooms in a lodge with pagination support

    def get_room_by_lodge_and_number(self, db: Session, room_no: str, lodge_id: int):
        """Retrieve a specific room by its room number."""

        return db.query(self.model).filter(
            self.model.lodge_id == lodge_id,
            self.model.room_no == room_no
        ).first()

    def get_rooms(self, db: Session, skip: int = 0, max_limit: int = 50):
        """Retrieve a list of rooms with pagination support."""
        stmt = select(self.model).join(Lodge).offset(skip).limit(limit=max_limit)
        return db.execute(stmt).scalars().all()


    def get_dashboard_rooms(
            self,
            db: Session,
            filter_by: DashboardFilters,
            lodge_id: int,
            skip: int = 0,
            limit: int = 50
    ) :

        stmt = (select(
            Lease.id.label('lease_id'),
            Room.room_no.label('room_no'),
            case(
                (and_(*const.filter_menu.get(BadgeTexts.SAFE)), BadgeTexts.SAFE),
                (and_(*const.filter_menu.get(BadgeTexts.EXPIRING)), BadgeTexts.EXPIRING),
                (and_(*const.filter_menu.get(BadgeTexts.OVERDUE)), BadgeTexts.OVERDUE),
                (and_(*const.filter_menu.get(BadgeTexts.OWING)), BadgeTexts.OWING),
                (const.vacant_expr, RoomStatus.VACANT),
                (const.maintenance_expr, RoomStatus.MAINTENANCE),
                else_='Unknown_badge_text'
            ).label('badge_text'),

            case(
                (and_(*const.filter_menu.get(BadgeTexts.SAFE)), BadgeVariants.SUCCESS),
                (and_(*const.filter_menu.get(BadgeTexts.EXPIRING)), BadgeVariants.WARNING),
                (and_(*const.filter_menu.get(BadgeTexts.OVERDUE)), BadgeVariants.DANGER),
                (and_(*const.filter_menu.get(BadgeTexts.OWING)), BadgeVariants.INFO),
                (const.vacant_expr, BadgeVariants.INACTIVE),
                (const.maintenance_expr, BadgeVariants.NEED_REPAIR),
                else_= 'Unknown_variant'
            ).label('badge_variant'),

            case(
                (const.occupied_expr, func.concat(User.first_name, ' ', User.last_name, )),
                (const.vacant_expr, 'Ready to Lease'),
                (const.maintenance_expr, 'Unavailable'),
                else_='Invalid'
            ).label('main_display_text'),

            case(
                (and_(*const.filter_menu.get(BadgeTexts.OVERDUE)),
                    func.concat(func.abs(const.days_left, ), 'days overdue')
                ),
                (const.occupied_expr, func.concat(const.days_left, 'days left')),
                (const.vacant_expr, 'Available'),
                (const.maintenance_expr, 'Under Maintenance'),
                else_='Invalid'
            ).label('sub_display_text'),

        ).select_from(
            Room
        ).outerjoin(
            Lease, and_(Lease.room_id == Room.id, Lease.status == LeaseStatus.ACTIVE)
        ).outerjoin(
            TenantProfile, Lease.tenant_id == TenantProfile.id
        ).outerjoin(
            User, TenantProfile.user_id == User.id
        ).outerjoin(
            const.payment_subq, const.payment_subq.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id
        ).group_by(
            Lease.id,
            User.first_name,
            User.last_name,
            Room.room_no,
            Lease.agreed_rent_amt,
            Lease.end_date,
            Room.status,

        ))

        #if filters dict is empty, fetch the list of categorized rooms with pagination support
        #otherwise only fetch the list of room categories that match the provided filters
        filtered_stmt = apply_dashboard_filters(filter_by=filter_by, filters=const.filter_menu, stmt=stmt)

        stmt = filtered_stmt.offset(skip).limit(limit)

        return db.execute(stmt).mappings().all()


crud_room = CRUDRoom(Room)
