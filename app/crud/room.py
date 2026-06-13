from typing import Union
from app.core.enums import RoomStatus, BadgeTexts, BadgeVariants
from app.crud.payment import crud_payment
from app.models.lease import Lease
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomGridSummary
from sqlalchemy.orm import Session
from app.crud.base_crud import CRUDBase
from sqlalchemy import func, select, case, and_


class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    #method to get room by lodge and number
    # method to get many rooms in a lodge with pagination support

    def get_room_by_lodge_and_number(self, db: Session, room_no: str, lodge_id: int):
        """Retrieve a specific room by its room number."""

        return db.query(self.model).filter(
            self.model.lodge_id == lodge_id,
            self.model.room_no == room_no
        ).first()

    def get_rooms(self, db: Session, lodge_id: int, skip: int = 0, max_limit: int = 50):
        """Retrieve a list of rooms with pagination support."""
        return db.query(self.model).filter(self.model.lodge_id == lodge_id).offset(skip).limit(max_limit).all()

    def get_dashboard_rooms(
            self,
            filter_by:
            Union[BadgeTexts, RoomStatus],
            db: Session,
            lodge_id: int,
            skip: int = 0,
            limit: int = 50
    ) :

        payment_subq = crud_payment.get_payment_subq()

        days_left = Lease.end_date - func.current_date()
        has_payed = func.sum(payment_subq.c.total_paid) == Lease.agreed_rent_amt
        not_payed = func.sum(payment_subq.c.total_paid) < Lease.agreed_rent_amt

        stmt = (select(
            Lease.id.label('lease_id'),
            Room.room_no.label('room_no'),
            case(
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 90, has_payed), BadgeTexts.SAFE),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 0, has_payed), BadgeTexts.EXPIRING),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left < 0, has_payed), BadgeTexts.OVERDUE),
                (Room.status == RoomStatus.VACANT, RoomStatus.VACANT),
                (Room.status == RoomStatus.MAINTENANCE, RoomStatus.MAINTENANCE),
                else_=BadgeTexts.OWING
            ).label('badge_text'),

            case(
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 90, has_payed), BadgeVariants.SUCCESS),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 0, has_payed), BadgeVariants.WARNING),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left < 0, has_payed), BadgeVariants.DANGER),
                (Room.status == RoomStatus.VACANT, BadgeVariants.INACTIVE),
                (Room.status == RoomStatus.MAINTENANCE, BadgeVariants.NEED_REPAIR),
                else_=BadgeVariants.INFO
            ).label('badge_variants'),

            case(
                (Room.status == RoomStatus.OCCUPIED, func.concat(User.first_name, User.last_name, 'full name')),
                (Room.status == RoomStatus.VACANT, 'Ready to Lease'),
                (Room.status == RoomStatus.MAINTENANCE, 'Unavailable'),
                else_='Invalid'
            ).label('main_display_text'),

            case(
                (Room.status == RoomStatus.OCCUPIED, func.concat(days_left, 'days left')),
                (Room.status == RoomStatus.VACANT, 'Available'),
                (Room.status == RoomStatus.MAINTENANCE, 'Under Maintenance'),
                else_='Invalid'
            ).label('sub_display_text'),

        ).select_from(
            Room
        ).outerjoin(
            Lease, Lease.room_id == Room.id
        ).outerjoin(
            TenantProfile, Lease.tenant_id == TenantProfile.id
        ).outerjoin(
            User, TenantProfile.user_id == User.id
        ).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id
        ).group_by(
            Lease.id,
            Room.room_no,
            Lease.end_date,
            Lease.agreed_rent_amt,
            Room.status,
            User.first_name,
            User.last_name
        ))


        if filter_by == BadgeTexts.SAFE:
            stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(has_payed, days_left >= 90)

        elif filter_by == BadgeTexts.EXPIRING:
            stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(has_payed, days_left >= 0)

        elif filter_by == BadgeTexts.OVERDUE:
            stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(has_payed, days_left < 0)

        elif filter_by == RoomStatus.VACANT:
            stmt = stmt.where((Room.status == RoomStatus.VACANT))

        elif filter_by == RoomStatus.MAINTENANCE:
            stmt = stmt.where((Room.status == RoomStatus.MAINTENANCE))

        elif filter_by == BadgeTexts.OWING:
            stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(not_payed)

        stmt = stmt.offset(skip).limit(limit)

        db_rooms = db.execute(stmt).mappings().all()
        rooms_summary = [RoomGridSummary(**row) for row in db_rooms]

        return rooms_summary


crud_room = CRUDRoom(Room)
