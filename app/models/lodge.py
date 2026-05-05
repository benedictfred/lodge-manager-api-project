from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime, Boolean
from app.db.session import Base
from sqlalchemy.orm  import relationship


class Lodge(Base):
    __tablename__ = 'lodges'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    landlord_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=True)
    owner = relationship('User', back_populates='lodges')
    rooms = relationship("Room", back_populates='lodge', cascade='all, delete-orphan')
    tenantprofiles = relationship('TenantProfile', back_populates='lodge', cascade='all, delete-orphan')

