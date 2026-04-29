from pydantic import BaseModel
from typing import Optional

from decimal import Decimal
from datetime import date

class PaymentBase(BaseModel):
    lease_id: int
    amount_paid: Decimal
    payment_date: date


class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int

    class Config:
        from_attributes = True

class PaymentUpdate(BaseModel):
    lease_id: Optional[int] = None
    amount_paid: Optional[Decimal] = None
    payment_date: Optional[date] = None
