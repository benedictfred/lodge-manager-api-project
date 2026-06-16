"""
TypedDict definitions for generic extra data.

This module contains definitions for generic dictionaries used to pass
around extra user information or context.
"""
from typing import TypedDict
from app.core.enums import UserRole

class GenericExtras(TypedDict):
    """
    A typed dictionary for generic extra user data.

    Attributes:
        role (UserRole): The user's role.
        landlord_id (int): The landlord's ID.
        lodge_id (int): The lodge's ID.
        hashed_password (str): The hashed password.
    """
    role: UserRole
    landlord_id: int
    lodge_id: int
    hashed_password: str