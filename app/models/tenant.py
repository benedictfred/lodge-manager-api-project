from app.db.session import  Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

# class Tenant(Base):
#     __tablename__ = 'tenants'
#
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     email = Column(String(50), nullable=False, unique=True, index=True)
#     phone_no = Column(String(20), nullable=False, unique=True, index=True)
#     leases = relationship('Lease', back_populates='tenant')
