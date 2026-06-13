from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from datetime import datetime


class PaymentBase(BaseModel):
    amount_paid: int = Field(..., ge=0)
    lease_id: int

class PaymentCreate(PaymentBase):
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime

    model_config = ConfigDict(from_attributes=True)