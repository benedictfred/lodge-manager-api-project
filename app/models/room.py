from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.db.session import Base
from sqlalchemy import Integer, Column, String,Enum, ForeignKey,DateTime
from app.core.enums import RoomStatus


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    lodge_id = Column(Integer, ForeignKey('lodges.id', ondelete='CASCADE'))
    room_no = Column(String, index=True, nullable=False)
    description = Column(String(300))
    base_rent_price = Column(Integer, nullable=False, default=200000)
    status = Column(Enum(RoomStatus), default=RoomStatus.VACANT, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    # leases = relationship('Lease', back_populates='room', cascade='all, delete-orphan')
    lodge = relationship('Lodge', back_populates='rooms')

    __table_args__ = (
        UniqueConstraint(
            'room_no',
            'lodge_id',
            name='lodge_room_uc'
        ),)
