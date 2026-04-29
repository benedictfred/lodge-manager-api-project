from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy import Integer, Column, String, Boolean, DateTime, func

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email= Column(String(256), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lodges = relationship('Lodge', back_populates='owner')
