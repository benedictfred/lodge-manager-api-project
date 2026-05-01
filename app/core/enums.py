from enum import Enum


class UserRole(str, Enum):
    LANDLORD = "landlord"
    TENANT = "tenant"
    ADMIN = "admin"

class RoomStatus(str, Enum):
    VACANT = 'Vacant'
    OCCUPIED = 'Occupied'
    MAINTENANCE = 'Maintenance'