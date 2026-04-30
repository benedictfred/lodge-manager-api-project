from datetime import  datetime
from typing import Optional

from pydantic import BaseModel


class LodgeBase(BaseModel):
    name: str
    address: str


class LodgeCreate(LodgeBase):
    pass

class LodgeResponse(LodgeBase):
    id: int
    landlord_id: int
    created_at: datetime
    is_active: bool

    model_config = {'from_attributes': True}


class LodgeUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

