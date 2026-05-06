from app.core.enums import TenantType, StudentLevel
from app.db.session import  Base
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lodge import Lodge

class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    lodge_id: Mapped[int] = mapped_column(Integer, ForeignKey('lodges.id', ondelete='CASCADE'), nullable=False, unique=True)
    tenant_type: Mapped[TenantType] = mapped_column(Enum(TenantType), nullable=False, default=TenantType.STUDENT)
    emergency_contact_name: Mapped[str] = mapped_column(String(20), nullable=False,  index=True)
    emergency_contact_phone_no: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[StudentLevel] = mapped_column(Enum(StudentLevel), nullable=True)
    department: Mapped[str] = mapped_column(String, nullable=True)
    reg_no: Mapped[str] = mapped_column(String, nullable=True)
    user: Mapped["User"] = relationship('User', back_populates='tenantprofile', cascade='all, delete-orphan', single_parent=True)
    lodge: Mapped["Lodge"] = relationship('Lodge', back_populates='tenantprofiles')
    # leases = relationship('Lease', back_populates='tenant')

    @property
    def is_active(self):
        return self.user.is_active if self.user else True

    @property
    def created_at(self):
        return self.user.created_at if self.user else None

    @property
    def role(self):
        return self.user.role if self.user else None