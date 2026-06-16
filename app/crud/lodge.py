"""
Module providing lodge-related CRUD operations.

This module contains the CRUD operations for Lodge models.
"""
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
    """
    CRUD class for Lodge model operations.
    """
    #method for getting lodge owned by a specific landlord
    def get_by_landlord(self, db: Session, landlord_id: int, lodge_id: int):
        """
        Get a specific lodge owned by a landlord.

        Args:
            db (Session): The database session.
            landlord_id (int): The ID of the landlord.
            lodge_id (int): The ID of the lodge.

        Returns:
            Lodge: The found lodge or None.
        """
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id, self.model.id == lodge_id
        ).first()

    #method to getting lodge owned by a specific landlord with a specific lodge name
    def get_by_name_and_landlord(self, db: Session, landlord_id: int, lodge_name: str):
        """
        Get a lodge by its name and landlord ID.

        Args:
            db (Session): The database session.
            landlord_id (int): The ID of the landlord.
            lodge_name (str): The name of the lodge to search for.

        Returns:
            Lodge: The found lodge or None.
        """
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
        """
        Get multiple lodges owned by a specific landlord.

        Args:
            db (Session): The database session.
            landlord_id (int): The ID of the landlord.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            List[Lodge]: A list of lodges owned by the landlord.
        """
        return db.query(self.model).filter(
            self.model.landlord_id == landlord_id
        ).offset(skip).limit(limit).all()

    def get_room_status_counts(self, db: Session, lodge_id: int):
        """
        Get the count of rooms by status in a specific lodge.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.

        Returns:
            RowMapping: The counts of occupied, vacant, and maintenance rooms.
        """
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
        """
        Get the total number of tenants in a specific lodge.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.

        Returns:
            RowMapping: The total tenant count.
        """
        tenant_count_expr = func.count(TenantProfile.id)
        stmt = select(tenant_count_expr.label('total_tenants')).where(TenantProfile.lodge_id == lodge_id)

        result = db.execute(stmt).mappings().first()
        return result

    def get_occupied_counts(self, db: Session, lodge_id: int):
        """
        Get the counts of occupied rooms categorized by payment/lease status.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.

        Returns:
            RowMapping: The counts of safe, expiring, overdue, and owing statuses.
        """


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

        pending_count_expr = func.count(
            case(
                (and_(*const.filter_menu.get(BadgeTexts.PENDING)), 1), else_=None
            )
        )

        stmt = select(
            safe_count_expr.label('safe'),
            expiring_count_expr.label('expiring'),
            overdue_expr.label('overdue'),
            pending_count_expr.label('pending'),
            owing_count_expr.label('owing')
        ).select_from(Lease).outerjoin(
            Room, Lease.room_id == Room.id
        ).outerjoin(
            const.PAYMENT_SUBQ, const.PAYMENT_SUBQ.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id,
            Lease.status.in_([LeaseStatus.ACTIVE, LeaseStatus.OVERDUE, LeaseStatus.PENDING_TERMINATION]),
            Room.status == RoomStatus.OCCUPIED
        )

        result = db.execute(stmt).mappings().first()
        return result




crud_lodge = CRUDLodge(Lodge)
