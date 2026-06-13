from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import func
from app.db.session import Base
from sqlalchemy import Integer, String, Enum, ForeignKey, DateTime
from app.core.enums import RoomStatus

from typing import TYPE_CHECKING

from app.schemas.room import RoomGridSummary

if TYPE_CHECKING:
    from app.models.lodge import Lodge
    from app.models.lease import Lease


class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True)
    lodge_id: Mapped[int] = mapped_column(ForeignKey('lodges.id', ondelete='CASCADE'))
    room_no: Mapped[str] = mapped_column(index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(300))
    base_rent_price: Mapped[int] = mapped_column(nullable=False, default=200000)
    status: Mapped["RoomStatus"] = mapped_column(Enum(RoomStatus), default=RoomStatus.VACANT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    leases: Mapped["Lease"] = relationship( back_populates='room')
    lodge: Mapped["Lodge"] = relationship( back_populates='rooms')

    __table_args__ = (
        UniqueConstraint(
            'room_no',
            'lodge_id',
            name='lodge_room_uc'
        ),)

@dataclass
class RoomFilter:
    safe: list[RoomGridSummary] = field(default_factory=list)
    expiring:  list[RoomGridSummary] = field(default_factory=list)
    overdue: list[RoomGridSummary] = field(default_factory=list)
    owing: list[RoomGridSummary] = field(default_factory=list)
    vacant: list[RoomGridSummary] = field(default_factory=list)
    maintenance: list[RoomGridSummary] = field(default_factory=list)
