from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from typing import Optional
from app.core.enums import TenantType, StudentLevel


class TenantBase(BaseModel):
    tenant_type: TenantType
    emergency_contact_name: str
    emergency_contact_phone_no: str
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None


class TenantProfileCreate(BaseModel):
    user_info: UserCreate
    tenant_info: TenantBase


class TenantProfileResponse(TenantBase):
    id: int
    user_id: int
    created_at: datetime
    is_active: bool
    lodge_id: int
    user: UserResponse

    model_config = {'from_attributes': True}


class TenantProfileUpdate(UserUpdate):
    tenant_type: Optional[TenantType] = None
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None
