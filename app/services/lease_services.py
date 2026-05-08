from typing import Optional

from app.core.enums import LeaseStatus
from app.crud.tenantprofile import crud_tenant
from app.models.user import User
from app.schemas import room as schema_room
from app.crud.room import crud_room
from sqlalchemy.orm import Session

from app.schemas.lease import LeaseCreate
from app.services import lodge_service, room_service
from app.crud.lease import crud_lease
from app.core.exceptions import RoomAlreadyExistError, RoomNotFoundError, UserNotFoundError, ActiveLeaseFoundError, \
        LodgeNotFoundError


def create_new_lease(
        db: Session,
        lease_data: LeaseCreate,
        landlord_user: User
):
    room = crud_room.get(db, item_id=lease_data.room_id)

    if not room:
        raise RoomNotFoundError()

    if room.lodge.landlord_id != landlord_user.id:
        raise RoomNotFoundError()

    tenant = crud_tenant.get(db, item_id=lease_data.tenant_id)

    if not tenant:
        raise UserNotFoundError()

    active_lease = crud_lease.get_active_room_and_tenant_lease(
        db,
        room_id=room.id,
        tenant_id=tenant.id
    )

    if active_lease:
        raise ActiveLeaseFoundError()

    return crud_lease.create_lease(db, lease_data=lease_data, room=room)


def filter_leases_for_landlord(
        db: Session,
        lodge_id: int,
        landlord_id: int,
        tenant_id: Optional[int] = None,
        room_id: Optional[int] = None,
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None
):

        lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

        if not lodge:
                raise LodgeNotFoundError()


        return filter_leases(
                db,
                tenant_id=tenant_id,
                room_id=room_id,
                skip=skip,
                max_limit=max_limit,
                status=status
        )

def filter_leases(
        db: Session,
        lodge_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        room_id: Optional[int] = None,
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None
):


    return crud_lease.get_tenant_leases(db, lodge_id=lodge_id, tenant_id=tenant_id,room_id=room_id, status=status, max_limit=max_limit, skip=skip)
