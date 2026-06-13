from multiprocessing.util import sub_debug

from sqlalchemy.orm import Session

from app.core.enums import LeaseStatus
from app.models.lease import Lease
from app.models.lodge import Lodge
from app.models.payment import Payment
from app.models.room import Room
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.crud.base_crud import CRUDBase
from sqlalchemy import func, select, case


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentResponse]):
    def get_payments_aggregate_by_lease_id(self, db: Session, lease_id: int):
        return db.query(func.sum(self.model.amount_paid)).filter(Payment.lease_id == lease_id).scalar()

    def get_lease_payments(self, db: Session, lease_id: int, skip: int = 0, limit: int = 50) -> list[type[Payment]]:
        return db.query(self.model).filter(self.model.lease_id == lease_id).offset(skip).limit(limit).all()

    def get_potential_income_from_rooms(self, db: Session, lodge_id: int):
        stmt = select(func.sum(Room.base_rent_price).label('potential_revenue').where(Room.lodge_id == lodge_id))

        return db.execute(stmt).scalar()
    def get_payment_subq(self):
        payment_subq = select(
            Payment.lease_id,
            func.sum(Payment.amount_paid).label('total_amt_paid')
        ).group_by(Payment.lease_id).subquery()

        return payment_subq
    def get_financials_for_active_leases(self, db: Session, lodge_id: int):
        #return the sum of agreed rent for active leases and payments for active leases
        #start from the lease table and go to the payment table
        payment_subq = self.get_payment_subq()

        stmt = (select(
            func.sum(Lease.agreed_rent_amt).label('expected_revenue'),
            func.sum(payment_subq.c.total_amt_paid).label('collected_revenue')

        ).select_from(Lease).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).where(Room.lodge_id == lodge_id, Lease.status == LeaseStatus.ACTIVE))


        return db.execute(stmt).mappings().all()

    def get_total_unpaid_rent(self, db: Session, lodge_id: int):
        stmt = select(
            case(func.sum(Lease.agreed_rent_amt) - func.sum(Payment.amount_paid)).label('unpaid_rent')
        ).where(Room.lodge_id == lodge_id)

        return db.execute(stmt).scalar()

crud_payment = CRUDPayment(Payment)
