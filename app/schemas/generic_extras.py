from typing import TypedDict
from app.core.enums import UserRole

class GenericExtras(TypedDict):
    role: UserRole
    landlord_id: int
