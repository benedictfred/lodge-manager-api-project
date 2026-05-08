from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from typing import Optional
from app.core.enums import TenantType, StudentLevel


class TenantBase(BaseModel):
    lodge_id: int
    tenant_type: TenantType
    emergency_contact_name: str
    emergency_contact_phone_no: str
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None


class TenantProfileCreate(BaseModel):
    user_info: UserCreate
    tenant_info: TenantBase


class TenantInfoUpdate(BaseModel):
    tenant_type: Optional[TenantType] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone_no: Optional[str] = None
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None

class TenantProfileResponse(TenantBase):
    id: int
    user_id: int
    created_at: datetime
    is_active: bool
    user: UserResponse

    model_config = {'from_attributes': True}


class TenantProfileUpdate(BaseModel):
    user_info: Optional[UserUpdate] = None
    tenant_info: Optional[TenantInfoUpdate] = None


