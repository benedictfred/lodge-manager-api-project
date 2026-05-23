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

