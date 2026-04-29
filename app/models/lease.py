from app.db.session import Base
from sqlalchemy import Integer, Date, Column, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
#
# class Lease(Base):
#     __tablename__ = 'leases'
#
#     id = Column(Integer, primary_key=True)
#     tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
#     room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
#     start_date = Column(Date, default=func.now(), nullable=False)
#     end_date = Column(Date, nullable=True)
#     agreed_rent_amt = Column(Numeric(10, 2))
#     is_active = Column(Boolean, default=True)
#     tenant = relationship('Tenant', back_populates='leases')
#     room = relationship('Room', back_populates='leases')
#     payments = relationship('Payment', back_populates='lease')

