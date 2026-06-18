"""
SQLAlchemy models for the user domain.

This module contains the User model which represents an application user,
such as a landlord or a tenant.
"""
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
    """
    Represents an application user (e.g., landlord or tenant).

    Attributes:
        id (int): Primary key.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        phone_no (str): The user's phone number.
        email (str): The user's email address.
        hashed_password (str): The user's hashed password.
        role (UserRole): The user's role in the system (e.g., LANDLORD, TENANT).
        created_at (datetime): Timestamp when the user was created.
        is_active (bool): Indicates if the user account is active.
        lodges (list[Lodge]): Relationship to the lodges owned by the user (if landlord).
        tenant_profile (TenantProfile): Relationship to the user's tenant profile (if tenant).
    """
    __tablename__ = 'users'

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
