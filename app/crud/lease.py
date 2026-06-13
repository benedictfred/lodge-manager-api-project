from sqlalchemy import select, Select
from typing import Optional
from sqlalchemy.orm import Session

from app.core.enums import LeaseStatus
from app.models.payment import Payment
from app.models.room import RoomStatus, Room
from app.schemas.lease import LeaseCreate, LeaseUpdate
from app.models.lease import Lease
from app.crud.base_crud import CRUDBase
from datetime import datetime


class CRUDLease(CRUDBase[Lease, LeaseCreate, LeaseUpdate]):

    def get_tenant_leases(
            self,
            db: Session,
            lodge_id: Optional[int] = None,
            tenant_id: Optional[int] = None,
            room_id: Optional[int] = None,
            status: Optional[LeaseStatus] = None,
            skip: int = 0,
            max_limit: int = 50
    ) -> list[Lease]:

        # 1. Initialize the statement
        stmt: Select = select(self.model)

        if lodge_id:
            stmt = stmt.join(Room).where(lodge_id=lodge_id)


        if tenant_id:
            stmt = stmt.filter_by(tenant_id=tenant_id)

        if room_id:
            stmt = stmt.filter_by(room_id=room_id)

        if status:
            stmt = stmt.filter_by(status=status)

        stmt = stmt.offset(skip).limit(max_limit)

        # 4. Execute
        result = db.execute(stmt)
        leases: list[Lease] = list(result.scalars().all())
        return leases


    def get_room_leases(self, db: Session, room_id: int, skip: int = 0, max_limit: int = 50) -> list[type[Lease]]:
        return db.query(self.model).filter(self.model.room_id == room_id).offset(skip).limit(max_limit).all()

    def create_lease(self, db: Session, lease_data: LeaseCreate, room: Room):
        #mark the room's status as occupied
        #stage the lease for commit
        #flush to get lease id for creating first payment record
        #add the lease id to the payment record
        #if anything fails while commit the record , fallback or rollback the transaction

        try:
            db_lease = Lease(**lease_data.model_dump(exclude={'total_amt_paid'}))
            db.add(db_lease)
            db.flush()

            db_payment = Payment(lease_id=db_lease.id, amount_paid=lease_data.total_amt_paid)
            db.add(db_payment)

            room.status = RoomStatus.OCCUPIED
            db.commit()
            db.refresh(db_lease)


        except Exception as e:
            db.rollback()
            raise e

        return db_lease

    def get_active_room_and_tenant_lease(self, db: Session, room_id: int, tenant_id: int):
        return db.query(self.model).filter(
            self.model.room_id == room_id,
            self.model.tenant_id == tenant_id,
            Lease.status == LeaseStatus.ACTIVE
        ).first()

    def lease_terminate(self, db: Session, db_lease: Lease) -> Lease:
        db_lease.status = LeaseStatus.TERMINATED
        db_lease.room.status = RoomStatus.VACANT
        db_lease.end_date = datetime.now()

        db.commit()
        db.refresh(db_lease)
        return db_lease


    def update_lease(self, db: Session, lease_data: LeaseUpdate, db_lease: Lease) -> Lease:
        update_data = lease_data.model_dump(exclude_unset=True)

        for k, v in update_data.items():
            setattr(db_lease, k, v)

        db.add(db_lease)
        db.commit()
        db.refresh(db_lease)
        return db_lease

    def  request_terminate_lease(self, db: Session, db_lease: Lease) -> Lease:
        db_lease.status = LeaseStatus.PENDING_TERMINATION
        db.commit()
        db.refresh(db_lease)
        return db_lease


crud_lease = CRUDLease(Lease)
