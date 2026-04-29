from sqlalchemy.sql import func
from sqlalchemy import Integer, Date, Numeric, Column, ForeignKey
from app.db.session import Base
from sqlalchemy.orm  import relationship

# class Payment(Base):
#     __tablename__ = 'payments'
#
#     id = Column(Integer, primary_key=True)
#     lease_id = Column(Integer, ForeignKey('leases.id'), nullable=False, index=True)
#     amount_paid = Column(Numeric(10,2), nullable=False)
#     payment_date = Column(Date, default=func.now(), nullable=False)
#     lease = relationship('Lease', back_populates='payments')