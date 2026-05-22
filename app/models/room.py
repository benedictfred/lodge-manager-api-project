from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import func
from app.db.session import Base
from sqlalchemy import Integer, String, Enum, ForeignKey, DateTime
from app.core.enums import RoomStatus

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lodge import Lodge
    from app.models.lease import Lease


class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lodge_id: Mapped[int] = mapped_column(Integer, ForeignKey('lodges.id', ondelete='CASCADE'))
    room_no: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(300))
    base_rent_price: Mapped[int] = mapped_column(Integer, nullable=False, default=200000)
    status: Mapped["RoomStatus"] = mapped_column(Enum(RoomStatus), default=RoomStatus.VACANT, nullable=False)
    created_at: Mapped['DateTime'] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    leases: Mapped["Lease"] = relationship('Lease', back_populates='room', )
    lodge: Mapped["Lodge"] = relationship("Lodge", back_populates='rooms')

    __table_args__ = (
        UniqueConstraint(
            'room_no',
            'lodge_id',
            name='lodge_room_uc'
        ),)


class RoomFilter:
    def __init__(self):
        self.safe = []
        self.expiring = []
        self.overdue = []
        self.owing = []
        self.vacant = []
        self.maintenance = []

