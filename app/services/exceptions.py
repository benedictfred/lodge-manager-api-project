
class UserAlreadyExistError(Exception):
    def __init__(self, email: str):
        super().__init__(f'User with with email {email} already exists')

