
class UserAlreadyExistError(Exception):
    def __init__(self, email: str):
        super().__init__(f'User with with email: {email} already exists')


class LodgeAlreadyExistError(Exception):
    def __init__(self, msg:str):
        super().__init__(msg)


class LodgeNotFoundError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)