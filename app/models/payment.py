"""
SQLAlchemy models for the payment domain.

This module contains the Payment model which represents a payment made
by a tenant towards a specific lease agreement.
"""
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import  ForeignKey, DateTime
from app.db.session import Base
from sqlalchemy.orm  import relationship, mapped_column, Mapped

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lease import Lease


class Payment(Base):
    """
    Represents a payment made towards a lease.

    Attributes:
        id (int): Primary key.
        lease_id (int): Foreign key to the associated lease.
        amount_paid (int): The amount paid in this transaction.
        payment_date (datetime): Timestamp when the payment was made.
        lease (list[Lease]): Relationship to the associated lease.
    """
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    lease_id: Mapped[int] =  mapped_column( ForeignKey('leases.id'), nullable=False, index=True)
    amount_paid: Mapped[int] = mapped_column(nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lease: Mapped[list["Lease"]] = relationship(back_populates='payments')