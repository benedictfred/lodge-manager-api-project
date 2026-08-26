from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import RoomStatus
from app.core.exceptions import InviteNotFoundError, RoomNotAvailableError, ActiveInviteAlreadyExistsError
from app.crud.invite import crud_invite
from app.models.invitation import Invite
from app.schemas import invitation as schema_invite
from app.services import room_service


def invite_tenant(db: Session, invite_in: schema_invite.InviteCreate, landlord_id: int):
    room = room_service.verify_room_existence(db, landlord_id=landlord_id, room_id=invite_in.room_id)

    if room.computed_status != RoomStatus.VACANT:
        raise RoomNotAvailableError(room_no=room.room_no, room_status=room.computed_status.value)

    active_invite = crud_invite.get_active_invite_for_room(db, room_id=room.id)
    if active_invite:
        raise ActiveInviteAlreadyExistsError(room_id=room.id)

    return crud_invite.add_invite_record(db, invite_in=invite_in)


def fetch_invite_record(db: Session, invite_id: UUID) -> Invite:
    invite_record = crud_invite.get_invite_record_by_id(db, invite_id=invite_id)

    if not invite_record:
        raise InviteNotFoundError(invite_id=invite_id)

    return invite_record