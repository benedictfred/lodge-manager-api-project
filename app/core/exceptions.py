
class UserAlreadyExistError(Exception):
    def __init__(self, email: str):
        super().__init__(f'User with with email: {email} already exists')


class LodgeAlreadyExistError(Exception):
    def __init__(self, name: str):
        super().__init__(f'Lodge with name: {name} already exists')


class LodgeNotFoundError(Exception):
    def __init__(self):
        super().__init__('Lodge not found')

class RoomNotFoundError(Exception):
    def __init__(self):
        super().__init__('Room not found')

class RoomAlreadyExistError(Exception):
    def __init__(self, room_name: str):
        super().__init__(f'Room with that name: {room_name} already exists')