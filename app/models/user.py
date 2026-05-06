from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base
from sqlalchemy import Integer, Column, String, Boolean, DateTime, func
from app.core.enums import UserRole
from sqlalchemy import Enum

if TYPE_CHECKING:
    from app.models.tenantprofile import TenantProfile
    from app.models.lodge import Lodge


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] =  mapped_column(String, nullable=True)
    email: Mapped[str]= mapped_column(String(256), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(20), nullable=True, unique=False, index=True)
    role: Mapped['UserRole'] = mapped_column(Enum(UserRole), default=UserRole.LANDLORD, nullable=False)
    created_at: Mapped['DateTime'] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lodges: Mapped[list["Lodge"]] = relationship('Lodge', back_populates='owner', cascade='all, delete-orphan')
    is_active = Column(Boolean, default=True, nullable=False)
    tenantprofile: Mapped[list["TenantProfile"]] = relationship(
        "TenantProfile",back_populates='user',
        cascade='all, delete-orphan',
        single_parent=True
    )
