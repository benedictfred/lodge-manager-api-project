from enum import Enum


class UserRole(str, Enum):
    LANDLORD = "landlord"
    TENANT = "tenant"
    ADMIN = "admin"

class RoomStatus(str, Enum):
    VACANT = 'Vacant'
    OCCUPIED = 'Occupied'
    MAINTENANCE = 'Maintenance'

class TenantType(str, Enum):
    STUDENT = 'student'
    OTHERS = 'others'

class StudentLevel(str, Enum):
    LEVEL_100 = '100'
    LEVEL_200 = '200'
    LEVEL_300 = '300'
    LEVEL_400 = '400'
    LEVEL_500 = '500'
    LEVEL_600 = '600'