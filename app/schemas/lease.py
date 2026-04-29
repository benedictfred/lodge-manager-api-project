from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date



class LeaseBase(BaseModel):
    tenant_id: int
    room_id: int
    agreed_rent_amt: Decimal = Field(..., ge=0 ,max_digits=10, decimal_places=2)
    is_active: bool = True
    start_date: date
    end_date: Optional[date] = None


class LeaseCreate(LeaseBase):
    pass


class LeaseResponse(LeaseBase):
    id: int

    class Config:
        from_attributes = True

class LeaseUpdate(BaseModel):
    tenant_id: Optional[int] = None
    room_id: Optional[int] = None
    agreed_rent_amt: Optional[Decimal]  = None
    is_active: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

