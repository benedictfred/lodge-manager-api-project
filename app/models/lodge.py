"""
SQLAlchemy models for the lodge domain.

This module contains the Lodge model which represents a building or property
owned by a landlord that contains rooms for rent.
"""
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from app.db.session import Base
from sqlalchemy.orm  import relationship,mapped_column, Mapped

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import  User
    from app.models.room import Room
    from app.models.tenantprofile import TenantProfile

class Lodge(Base):
    """
    Represents a lodge or property containing rentable rooms.

    Attributes:
        id (int): Primary key.
        name (str): The name of the lodge.
        address (str): The physical address of the lodge.
        landlord_id (int): Foreign key to the user (landlord) who owns the lodge.
        created_at (datetime): Timestamp when the lodge was created.
        is_active (bool): Indicates if the lodge is currently active.
        owner (User): Relationship to the user who owns the lodge.
        rooms (list[Room]): Relationship to the rooms within the lodge.
        tenantprofiles (list[TenantProfile]): Relationship to the tenant profiles associated with this lodge.
    """
    __tablename__ = 'lodges'

    id: Mapped[int] = mapped_column( primary_key=True)
    name: Mapped[str] = mapped_column( nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    landlord_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    owner: Mapped["User"] = relationship(back_populates='lodges')
    rooms: Mapped[list["Room"]] = relationship(back_populates='lodge', cascade='all, delete-orphan')
    tenantprofiles: Mapped[list["TenantProfile"]] = relationship( back_populates='lodge', cascade='all, delete-orphan')

