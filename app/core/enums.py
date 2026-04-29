from enum import Enum


class UserRole(str, Enum):
    LANDLORD = "landlord"
    TENANT = "tenant"
    ADMIN = "admin"