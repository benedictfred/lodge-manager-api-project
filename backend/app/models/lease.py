"""
SQLAlchemy models for the lease domain.

This module contains the Lease model which represents a rental agreement
between a tenant and a landlord for a specific room.
"""
from datetime import date, datetime
from app.core.enums import LeaseStatus
from app.db.session import Base
from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.tenantprofile import TenantProfile
    from app.models.room import Room
    from app.models.payment import Payment


class Lease(Base):
    """
    Represents a lease agreement for a room.

    Attributes:
        id (int): Primary key.
        tenant_id (int): Foreign key to the tenant profile.
        room_id (int): Foreign key to the room being leased.
        start_date (date): The start date of the lease.
        end_date (date): The end date of the lease.
        agreed_rent_amt (int): The agreed rental amount for the lease duration.
        status (LeaseStatus): The current status of the lease (e.g., ACTIVE, EXPIRED).
        tenant (TenantProfile): Relationship to the tenant profile.
        room (Room): Relationship to the leased room.
        created_at (datetime): Timestamp when the lease was created.
        payments (list[Payment]): Relationship to the payments made under this lease.
    """
    __tablename__ = 'leases'

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenant_profiles.id'), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey('rooms.id'), nullable=False)
    start_date: Mapped[date] = mapped_column( nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    agreed_rent_amt: Mapped[int] = mapped_column( nullable=False)
    status: Mapped[LeaseStatus] = mapped_column(Enum(LeaseStatus), default=LeaseStatus.ACTIVE)
    tenant: Mapped["TenantProfile"] = relationship(back_populates='leases')
    room: Mapped["Room"] = relationship(back_populates='leases')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payments: Mapped[list["Payment"]] = relationship(back_populates='lease')

