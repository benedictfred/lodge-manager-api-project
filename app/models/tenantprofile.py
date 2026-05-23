from app.core.enums import TenantType, StudentLevel
from app.db.session import  Base
from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.lodge import Lodge
    from app.models.lease import Lease


class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    lodge_id: Mapped[int] = mapped_column(ForeignKey('lodges.id', ondelete='CASCADE'), nullable=False)
    tenant_type: Mapped[TenantType] = mapped_column(Enum(TenantType), nullable=False, default=TenantType.STUDENT)
    emergency_contact_name: Mapped[str] = mapped_column(String(20), nullable=False,  index=True)
    emergency_contact_phone_no: Mapped[str] = mapped_column(nullable=False)
    level: Mapped[StudentLevel | None] = mapped_column(Enum(StudentLevel), nullable=True)
    department: Mapped[str | None] = mapped_column(nullable=True)
    reg_no: Mapped[str | None] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates='tenant_profile', cascade='all, delete-orphan', single_parent=True)
    lodge: Mapped["Lodge"] = relationship(back_populates='tenantprofiles')
    leases: Mapped["Lease"] = relationship(back_populates='tenant')

    @property
    def is_active(self):
        return self.user.is_active if self.user else True

    @property
    def created_at(self):
        return self.user.created_at if self.user else None

    @property
    def role(self):
        return self.user.role if self.user else None