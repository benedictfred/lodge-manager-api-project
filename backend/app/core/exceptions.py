from typing import Optional, Any

from starlette import status

from app.core.enums import LeaseStatus, RoomStatus


class BaseLodgeOpsError(Exception):
    def __init__(self, detail: str, meta: dict = None, status_code: int = 400 ):
        self.status_code = status_code
        self.detail = detail
        self.meta = meta or {}
        super().__init__(self.detail)


class BaseAlreadyExistError(BaseLodgeOpsError):
    def __init__(self, entity_name: Optional[str], exception_name: str):
        self.entity_name = entity_name
        self.exception_name = exception_name
        self.detail = f'{self.exception_name.title()}: {self.entity_name} already exists'
        super().__init__(self.detail, status_code=400)


class UserAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, email: str):
        super().__init__(entity_name=email, exception_name='User')


class LodgeAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, name: str):
        super().__init__(entity_name=name, exception_name='Lodge')

class RoomAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, room_name: str):
        super().__init__(entity_name=room_name, exception_name='Room')





class InvalidLeaseActionError(BaseLodgeOpsError):
    def __init__(self, status: LeaseStatus ):
        self.detail = f'Lease is already {status.value}'
        super().__init__(detail=self.detail, status_code=400)


class BaseMaxLimitReachedError(BaseLodgeOpsError):
    def __init__(self, detail: str, meta: dict = None):
        super().__init__(detail=detail, status_code=400, meta=meta)

class RentAmtExceededError(BaseMaxLimitReachedError):
    def __init__(self, agreed, current_total, attempted):
        self.remaining = agreed - current_total
        self.detail = f"Remaining balance is ₦{self.remaining:,}. You attempted to pay ₦{attempted:,}."
        self.meta  = {
            'remaining': self.remaining,
            'current_total': current_total,
            'agreed_rent': agreed
        }
        super().__init__(detail=self.detail, meta=self.meta)


class BaseNotFoundError(BaseLodgeOpsError):
    def __init__(self, name:str):
        self.detail = f'{name.title()} could not be found'
        super().__init__(detail=self.detail, status_code=404, meta=self.meta)
        
        
class UserNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name="User")

class LodgeNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Lodge')


class RoomNotFoundError(BaseNotFoundError):
    def __init__(self, room_no: str = None):
        self.meta = {
            'room_no': room_no
        }
        super().__init__(name='Room' )

class LeaseNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Lease')

class TenantProfileNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='TenantProfile')


class UnauthorizedAccessError(BaseLodgeOpsError):
    def __init__(self):
        self.detail = f'Invalid email or password.'
        super().__init__(detail=self.detail, status_code=401)
        

class BaseNotAllowedError(BaseLodgeOpsError):
    def __init__(self, entity_name):
        self.detail = f'Only {entity_name} are allowed.'
        super().__init__(detail=self.detail, status_code=403)


class NotLandlordError(BaseNotAllowedError):
    def __init__(self):
        super().__init__(entity_name='landlords')


class NotTenantError(BaseNotAllowedError):
    def __init__(self):
        super().__init__(entity_name='tenants')

class InvalidCredentialsError(BaseLodgeOpsError):
    def __init__(self):
        self.detail = 'could not validate credentials'
        super().__init__(detail=self.detail, status_code=status.HTTP_401_UNAUTHORIZED)

class RoomIsOccupiedError(BaseLodgeOpsError):
    def __init__(self, occupied_room_no: str):
        self.detail = "Cannot update an occupied room. Terminate the lease first."
        self.meta = {
            'occupied_room_no ': occupied_room_no
        }

        super().__init__(detail=self.detail, status_code=status.HTTP_400_BAD_REQUEST, meta=self.meta)

class NotUpdatableOptionError(BaseLodgeOpsError):
    def __init__(self, update_status: RoomStatus, allowed_options: list[RoomStatus]):
        self.message = f'{update_status.value} is not an updatable option'

        self.meta = {
            'provided': f'{update_status.value}' ,
            'allowed_options': ', '.join([opt.value for opt in allowed_options])
        }
        super().__init__(detail=self.message, status_code=status.HTTP_400_BAD_REQUEST)