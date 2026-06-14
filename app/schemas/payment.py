"""
Pydantic schemas for the payment domain.

This module contains schemas used to represent, create, and update payment records.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from datetime import datetime


class PaymentBase(BaseModel):
    """
    Base schema for a payment.

    Attributes:
        amount_paid (int): The amount paid.
        lease_id (int): The ID of the lease this payment is for.
    """
    amount_paid: int = Field(..., ge=0)
    lease_id: int

class PaymentCreate(PaymentBase):
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime

    model_config = ConfigDict(from_attributes=True)