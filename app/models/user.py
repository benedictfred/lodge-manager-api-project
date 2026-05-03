from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy import Integer, Column, String, Boolean, DateTime, func
from app.core.enums import UserRole
from sqlalchemy import Enum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email= Column(String(256), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_no = Column(String(20), nullable=False, unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.LANDLORD, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lodges = relationship('Lodge', back_populates='owner', cascade='all, delete-orphan')
    is_active = Column(Boolean, default=True, nullable=False)
    tenant_profile = relationship('TenantProfile', back_populates='user')
