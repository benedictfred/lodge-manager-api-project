from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base
from sqlalchemy import String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from typing import TYPE_CHECKING
from app.core.enums import UserRole

if TYPE_CHECKING:
    from app.models.tenantprofile import TenantProfile
    from app.models.lodge import Lodge



class User(Base):
    __tablename__ = 'users'  # Fixed missing underscores

    id: Mapped[int] = mapped_column(primary_key=True)

    # Fixed: Added | None to match nullable=True
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    phone_no: Mapped[str] = mapped_column(String(20), nullable=False, unique=False, index=True)

    email: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    # Fixed: Removed quotes if UserRole is imported, IDEs prefer the actual class
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.LANDLORD, nullable=False)

    # Fixed: Used Python's datetime type instead of SQLAlchemy's DateTime string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                          nullable=False)

    # Fixed: Updated to 2.0 mapped_column to resolve the InstrumentedAttribute error
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    lodges: Mapped[list["Lodge"]] = relationship(back_populates='owner', cascade='all, delete-orphan')
    tenant_profile: Mapped["TenantProfile"] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        single_parent=True
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'