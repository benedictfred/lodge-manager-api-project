from pydantic import BaseModel
from typing import Optional

from pydantic import EmailStr, Field


class TenantBase(BaseModel):
    first_name: str
    last_name: str
    phone_no: str = Field(..., max_length=15)
    email: EmailStr

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantCreate):
    id: int

    class Config:
        from_attributes = True

class TenantUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_no: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None

