from typing import Optional

from app.core.enums import LeaseStatus


class BaseAlreadyExistError(Exception):
    def __init__(self, entity_name: Optional[str], exception_name: str):
        self.entity_name = entity_name
        self.exception_name = exception_name
        self.detail = f'{self.exception_name.title()}: {self.entity_name} already exists'
        super().__init__(self.detail)


class UserAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, email: str):
        super().__init__(entity_name=email, exception_name='User')


class LodgeAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, name: str):
        super().__init__(entity_name=name, exception_name='Lodge')

class RoomAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, room_name: str):
        super().__init__(entity_name=room_name, exception_name='Room')





class InvalidLeaseActionError(Exception):
    def __init__(self, status: LeaseStatus ):
        self.detail = f'Lease is already {status.value}'


class BaseMaxLimitReachedError(Exception):
    def __init__(self):
        pass

class RentAmtExceededError(BaseMaxLimitReachedError):
    def __init__(self, agreed, current_total, attempted):
        self.remaining = agreed - current_total
        self.detail = f"Remaining balance is ₦{self.remaining:,}. You attempted to pay ₦{attempted:,}."


class BaseNotFoundError(Exception):
    def __init__(self, name:str):
        self.detail = f'{name.title()} could not be found'
        
        
class UserNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name="User")

class LodgeNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Lodge')


class RoomNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Room')

class LeaseNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Lease')






class UnauthorizedAccessError(Exception):
    def __init__(self):
        self.detail = f'Invalid email or password.'
        

    