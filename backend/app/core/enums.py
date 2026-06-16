from enum import Enum


class UserRole(str, Enum):
    LANDLORD = "Landlord"
    TENANT = "Tenant"
    ADMIN = "Admin"


class RoomStatus(str, Enum):
    VACANT = 'Vacant'
    OCCUPIED = 'Occupied'
    MAINTENANCE = 'Maintenance'


class TenantType(str, Enum):
    STUDENT = 'Student'
    OTHERS = 'Others'


class StudentLevel(str, Enum):
    LEVEL_100 = '100'
    LEVEL_200 = '200'
    LEVEL_300 = '300'
    LEVEL_400 = '400'
    LEVEL_500 = '500'
    LEVEL_600 = '600'


class LeaseStatus(str, Enum):
    ACTIVE = 'Active'
    OVERDUE = 'Overdue'
    TERMINATED = 'Terminated'
    PENDING_TERMINATION = 'Pending_Termination'


class BadgeTexts(str, Enum):
    SAFE = 'Safe'
    EXPIRING = 'Expiring'
    OVERDUE = 'Overdue'
    OWING = 'Owing'
    PENDING = 'Pending'
    UNKNOWN_BADGE_TEXT = 'Unknown_badge_text'

class BadgeVariants(str, Enum):
    SUCCESS = 'Success'
    WARNING = 'Warning'
    DANGER = 'Danger'
    ORANGE = 'Orange'
    INACTIVE = 'Inactive'
    INFO = 'Info'
    PURPLE = 'Purple'
    UNKNOWN_VARIANT = 'Unknown_variant'
