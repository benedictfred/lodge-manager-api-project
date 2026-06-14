"""
Module providing payment-related CRUD operations.

This module contains the CRUD operations for Payment models.
"""
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
    """
    CRUD class for Payment model operations.
    """
    def get_payments_aggregate_by_lease_id(self, db: Session, lease_id: int):
        """
        Get the aggregated payment amount for a lease.

        Args:
            db (Session): The database session.
            lease_id (int): The ID of the lease.

        Returns:
            int: The total amount paid for the lease.
        """
        amt_paid_expr = func.coalesce(func.sum(self.model.amount_paid), 0)
        total_payments: int = db.query(amt_paid_expr).filter(Payment.lease_id == lease_id).scalar()
        return total_payments

    def get_lease_payments(self, db: Session, lease_id: int, skip: int = 0, limit: int = 50) -> list[type[Payment]]:
        """
        Get all payments for a specific lease.

        Args:
            db (Session): The database session.
            lease_id (int): The ID of the lease.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 50.

        Returns:
            list[type[Payment]]: A list of payments for the lease.
        """
        return db.query(self.model).filter(self.model.lease_id == lease_id).offset(skip).limit(limit).all()

    def get_potential_income_from_rooms(self, db: Session, lodge_id: int):
        """
        Get the potential income from all rooms in a lodge.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.

        Returns:
            int: The potential revenue from all rooms.
        """
        stmt = select(func.coalesce(func.sum(Room.base_rent_price), 0).label('potential_revenue')).where(Room.lodge_id == lodge_id)

        return db.execute(stmt).scalar()

    def get_payment_subq(self):
        """
        Create a subquery for aggregated payment amounts per lease.

        Returns:
            Subquery: The SQLAlchemy subquery object.
        """
        total_payment_expr = func.coalesce(func.sum(Payment.amount_paid), 0)
        payment_subq = select(
            Payment.lease_id,
            total_payment_expr.label('total_amt_paid')
        ).group_by(Payment.lease_id).subquery()

        return payment_subq

    def get_financials_for_active_leases(self, db: Session, lodge_id: int, filter_by: DashboardFilters):
        """
        Get financial metrics for active leases in a lodge.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.
            filter_by (DashboardFilters): Dashboard filters to apply.

        Returns:
            RowMapping: The expected and collected revenue.
        """
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
        """
        Get the total amount of unpaid rent in a lodge.

        Args:
            db (Session): The database session.
            lodge_id (int): The ID of the lodge.
            filter_by (DashboardFilters): Dashboard filters to apply.

        Returns:
            int: The total unpaid rent amount.
        """
        payment_subq = self.get_payment_subq()
        agreed_rent_expr = func.coalesce(func.sum(Lease.agreed_rent_amt), 0)
        total_paid_expr = func.coalesce(func.sum(payment_subq.c.total_amt_paid), 0)

        stmt = select(
            (agreed_rent_expr - total_paid_expr).label('unpaid_rent')
        ).select_from(
            Lease
        ).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).join(
            Room, Lease.room_id == Room.id
        ).where(
            Room.lodge_id == lodge_id,
            Lease.status == LeaseStatus.ACTIVE
        )

        stmt = apply_dashboard_filters(filter_by=filter_by, stmt=stmt, filters=constants.filter_menu)

        return db.execute(stmt).scalar()


crud_payment = CRUDPayment(Payment)
