"""
Module providing lease-related CRUD operations.

This module contains the CRUD operations for Lease models.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.core.enums import LeaseStatus
from app.models.payment import Payment
from app.models.room import RoomStatus, Room
from app.models.tenantprofile import TenantProfile
from app.schemas.lease import LeaseCreate, LeaseUpdate
from app.models.lease import Lease
from app.crud.base_crud import CRUDBase
from datetime import datetime, date
from sqlalchemy import select

class CRUDLease(CRUDBase[Lease, LeaseCreate, LeaseUpdate]):
    """
    CRUD class for Lease model operations.
    """

    def get_tenant_leases(
            self,
            db: Session,
            lodge_id: Optional[int] = None,
            tenant_id: Optional[int] = None,
            room_id: Optional[int] = None,
            status: Optional[LeaseStatus] = None,
            skip: Optional[int] = None,
            max_limit: Optional[int] = None
    ) -> list[Lease]:
        """
        Get leases for a tenant with optional filtering.

        Args:
            db (Session): The database session.
            lodge_id (Optional[int]): The ID of the lodge. Defaults to None.
            tenant_id (Optional[int]): The ID of the tenant. Defaults to None.
            room_id (Optional[int]): The ID of the room. Defaults to None.
            status (Optional[LeaseStatus]): The status of the lease. Defaults to None.
            skip (Optional[int]): Number of records to skip. Defaults to None.
            max_limit (Optional[int]): Maximum number of records to return. Defaults to None.

        Returns:
            list[Lease]: A list of retrieved leases.
        """

        # 1. Initialize the statement
        stmt = select(Lease).select_from(Lease).join(TenantProfile).join(Room)

        if tenant_id:
            stmt = stmt.where(TenantProfile.id == tenant_id)

        if room_id:
            stmt = stmt.where(Room.id == room_id)

        if status:
            stmt = stmt.where(Lease.status == status)

        stmt = stmt.where(Room.lodge_id == lodge_id).offset(skip).limit(max_limit)

        # 4. Execute
        result = db.execute(stmt)
        leases: list[Lease] = list(result.scalars().all())
        return leases


    def get_room_leases(self, db: Session, room_id: int, skip: int = 0, max_limit: int = 50) -> list[type[Lease]]:
        """
        Get leases for a specific room.

        Args:
            db (Session): The database session.
            room_id (int): The ID of the room.
            skip (int, optional): Number of records to skip. Defaults to 0.
            max_limit (int, optional): Maximum number of records to return. Defaults to 50.

        Returns:
            list[type[Lease]]: A list of leases for the room.
        """
        return db.query(self.model).filter(self.model.room_id == room_id).offset(skip).limit(max_limit).all()

    def create_lease(self, db: Session, lease_data: LeaseCreate, room: Room):
        """
        Create a new lease and associated initial payment.

        Args:
            db (Session): The database session.
            lease_data (LeaseCreate): The lease creation data.
            room (Room): The room being leased.

        Returns:
            Lease: The newly created lease.
        """
        #mark the room's status as occupied if in occupied allowed status
        #stage the lease for commit
        #flush to get lease id for creating first payment record
        #add the lease id to the payment record
        #if anything fails while commit the record , fallback or rollback the transaction
        _occupied_allowed_statuses = [LeaseStatus.ACTIVE, LeaseStatus.PENDING_TERMINATION, LeaseStatus.OVERDUE]
        try:
            db_lease = Lease(**lease_data.model_dump(exclude={'total_amt_paid'}))
            db.add(db_lease)
            db.flush()

            db_payment = Payment(lease_id=db_lease.id, amount_paid=lease_data.total_amt_paid)
            db.add(db_payment)

            room.status = RoomStatus.OCCUPIED if db_lease.computed_status in _occupied_allowed_statuses else RoomStatus.VACANT
            db.commit()
            db.refresh(db_lease)


        except Exception as e:
            db.rollback()
            raise e

        return db_lease

    def get_active_room_and_tenant_lease(self, db: Session, room_id: int, tenant_id: int):
        """
        Get an active lease for a specific room and tenant.

        Args:
            db (Session): The database session.
            room_id (int): The ID of the room.
            tenant_id (int): The ID of the tenant.

        Returns:
            Lease: The active lease or None.
        """
        return db.query(self.model).filter(
            self.model.room_id == room_id,
            self.model.tenant_id == tenant_id,
            self.model.status.is_(None),
            self.model.end_date >= date.today()
        ).first()

    def lease_terminate(self, db: Session, db_lease: Lease) -> Lease:
        """
        Terminate an active lease.

        Args:
            db (Session): The database session.
            db_lease (Lease): The lease to terminate.

        Returns:
            Lease: The terminated lease.
        """
        db_lease.status = LeaseStatus.TERMINATED
        db_lease.room.status = RoomStatus.VACANT
        db_lease.end_date = datetime.now()

        db.commit()
        db.refresh(db_lease)
        return db_lease



    def  request_terminate_lease(self, db: Session, db_lease: Lease) -> Lease:
        """
        Request termination for a lease.

        Args:
            db (Session): The database session.
            db_lease (Lease): The lease to request termination for.

        Returns:
            Lease: The updated lease.
        """
        db_lease.status = LeaseStatus.PENDING_TERMINATION
        db.commit()
        db.refresh(db_lease)
        return db_lease


crud_lease = CRUDLease(Lease)
