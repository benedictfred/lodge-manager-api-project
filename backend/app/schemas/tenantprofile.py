"""
Pydantic schemas for the tenant profile domain.

This module contains schemas used to represent, create, and update tenant profiles.
"""
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from typing import Optional
from app.core.enums import TenantType, StudentLevel


class TenantBase(BaseModel):
    """
    Base schema for a tenant profile.

    Attributes:
        lodge_id (int): The ID of the lodge where the tenant resides.
        tenant_type (TenantType): The type of tenant.
        emergency_contact_name (str): The name of the emergency contact.
        emergency_contact_phone_no (str): The phone number of the emergency contact.
        level (Optional[StudentLevel]): The academic level if the tenant is a student.
        reg_no (Optional[int]): The registration number.
        department (Optional[str]): The academic department.
    """
    lodge_id: int
    tenant_type: TenantType
    emergency_contact_name: str
    emergency_contact_phone_no: str
    level: Optional[StudentLevel] = None
    reg_no: Optional[int] = None
    department: Optional[str] = None

    @field_validator('emergency_contact_name', 'emergency_contact_phone_no',
                     mode='before')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()


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


