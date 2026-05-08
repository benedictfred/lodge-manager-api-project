from datetime import date

from app.core.enums import LeaseStatus
from app.db.session import Base
from sqlalchemy import Integer, Date,  ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from app.models.tenantprofile import TenantProfile
    from app.models.room import Room
    from app.models.payment import Payment


class Lease(Base):
    __tablename__ = 'leases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey('tenant_profiles.id'), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey('rooms.id'), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    agreed_rent_amt: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[LeaseStatus] = mapped_column(Enum(LeaseStatus), default=LeaseStatus.ACTIVE)
    tenant: Mapped["TenantProfile"] = relationship('TenantProfile', back_populates='leases')
    room: Mapped["Room"] = relationship('Room', back_populates='leases')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payments: Mapped["Payment"] = relationship('Payment', back_populates='lease')

