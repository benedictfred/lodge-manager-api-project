from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import  ForeignKey, DateTime
from app.db.session import Base
from sqlalchemy.orm  import relationship, mapped_column, Mapped

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lease import Lease


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    lease_id: Mapped[int] =  mapped_column( ForeignKey('leases.id'), nullable=False, index=True)
    amount_paid: Mapped[int] = mapped_column(nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lease: Mapped[list["Lease"]] = relationship(back_populates='payments')