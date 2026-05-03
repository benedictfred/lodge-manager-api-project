from app.schemas.user import UserCreate, UserUpdate
from typing import Optional
from app.core.enums import TenantType, StudentLevel
from pydantic import EmailStr, Field


class TenantBase(UserCreate):
    tenant_type: TenantType


class TenantProfileCreate(TenantBase):
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None


class TenantProfileResponse(TenantProfileCreate):
    id: int
    is_active: bool
    created_at: datetime
    role: UserRole

    class Config:
        from_attributes = True


class TenantProfileUpdate(UserUpdate):
    tenant_type: Optional[TenantType] = None
    level = Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None
