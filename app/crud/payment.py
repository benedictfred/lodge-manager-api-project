from sqlalchemy.orm import Session

from app.core import constants
from app.core.enums import LeaseStatus
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.room import Room
from app.schemas.dashboard import DashboardFilters
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.crud.base_crud import CRUDBase
from sqlalchemy import func, select

from utilities.dashboard_utilities import apply_dashboard_filters


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentResponse]):
    def get_payments_aggregate_by_lease_id(self, db: Session, lease_id: int):
        amt_paid_expr = func.coalesce(func.sum(self.model.amount_paid), 0)
        total_payments: int = db.query(amt_paid_expr).filter(Payment.lease_id == lease_id).scalar()
        return total_payments

    def get_lease_payments(self, db: Session, lease_id: int, skip: int = 0, limit: int = 50) -> list[type[Payment]]:
        return db.query(self.model).filter(self.model.lease_id == lease_id).offset(skip).limit(limit).all()

    def get_potential_income_from_rooms(self, db: Session, lodge_id: int):
        stmt = select(func.sum(Room.base_rent_price).label('potential_revenue')).where(Room.lodge_id == lodge_id)

        return db.execute(stmt).scalar()

    def get_payment_subq(self):
        total_payment_expr = func.coalesce(func.sum(Payment.amount_paid), 0)
        payment_subq = select(
            Payment.lease_id,
            total_payment_expr.label('total_amt_paid')
        ).group_by(Payment.lease_id).subquery()

        return payment_subq

    def get_financials_for_active_leases(self, db: Session, lodge_id: int, filter_by: DashboardFilters):
        payment_subq = self.get_payment_subq()

        expected_revenue_expr = func.coalesce(func.sum(Lease.agreed_rent_amt), 0)
        collected_revenue_expr = func.coalesce(func.sum(payment_subq.c.total_amt_paid), 0)

        stmt = (select(
            expected_revenue_expr.label('expected_revenue'),
            collected_revenue_expr.label('collected_revenue')

        ).select_from(Lease).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).join(
            Room, Room.id == Lease.room_id
        ).where(
            Room.lodge_id == lodge_id, Lease.status == LeaseStatus.ACTIVE
        ))

        stmt = apply_dashboard_filters(filter_by=filter_by, stmt=stmt, filters=constants.filter_menu)

        return db.execute(stmt).mappings().first()

    def get_total_unpaid_rent(self, db: Session, lodge_id: int, filter_by: DashboardFilters):
        payment_subq = self.get_payment_subq()
        agreed_rent_expr = func.coalesce(func.sum(Lease.agreed_rent_amt), 0)
        total_paid_expr = func.coalesce(func.sum(payment_subq.c.total_amt_paid), 0)

        stmt = select(
            (agreed_rent_expr - total_paid_expr).label('unpaid_rent')
        ).select_from(Lease).join(
            payment_subq, payment_subq.c.lease_id == Lease.id).join(
            Room, Lease.room_id == Room.id).where(Room.lodge_id == lodge_id)

        stmt = apply_dashboard_filters(filter_by=filter_by, stmt=stmt, filters=constants.filter_menu)

        return db.execute(stmt).scalar()


crud_payment = CRUDPayment(Payment)
