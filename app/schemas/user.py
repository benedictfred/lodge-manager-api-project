from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.core.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr

    @field_validator('email', mode='before')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip().lower()


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    role: UserRole

    model_config = {'from_attributes': True}

class UserUpdate(BaseModel):
    pass