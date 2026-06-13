from typing import Optional
from app.core.enums import LeaseStatus
from app.crud.tenantprofile import crud_tenant
from app.models.lease import Lease
from app.models.user import User
from app.crud.room import crud_room
from sqlalchemy.orm import Session
from app.schemas.lease import LeaseCreate
from app.services import lodge_service
from app.crud.lease import crud_lease
from app.core.exceptions import (RoomNotFoundError, UserNotFoundError,
                                 LodgeNotFoundError, LeaseNotFoundError,  InvalidLeaseActionError)


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
        raise InvalidLeaseActionError(status=active_lease.status)

    return crud_lease.create_lease(db, lease_data=lease_data, room=room)


def get_filtered_landlord_leases(
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
        lodge_id = lodge_id,
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
    return crud_lease.get_tenant_leases(
        db,
        lodge_id=lodge_id,
        tenant_id=tenant_id,
        room_id=room_id,
        status=status,
        max_limit=max_limit,
        skip=skip
    )

def verify_lease_to_terminate(
        db: Session,
        lease_id: int,
):
    lease = crud_lease.get(db, item_id=lease_id)
    if not lease:
        raise LeaseNotFoundError()

    # lease cannot be terminated if it has already been terminated or is expired
    if lease.status in [LeaseStatus.TERMINATED, LeaseStatus.EXPIRED]:
        raise InvalidLeaseActionError(status=lease.status)

    return lease

def terminate_lease(
        db: Session,
        lease_id: int,
        landlord_id: int,
):
    #find the lease with that id
    #use the room_id to find the room associated with that lease
    #check if the landlord owns the lodge the current found room is in
    #if all checks are done and the landlord does own the lodge , terminate the lease

    lease = verify_lease_to_terminate(db, lease_id=lease_id)

    room = lease.room

    if room.lodge.landlord_id != landlord_id:
        raise RoomNotFoundError()

    return crud_lease.lease_terminate(db, db_lease=lease)


def appeal_for_lease_termination(
        db:Session,
        lease_id: int,
        tenant_id: int
):
    #find lease with that id,
    #verify that the lease is terminatable
    #verify lease's tenant_id matches that of the current tenant
    #appeal for lease termination

    lease = verify_lease_to_terminate(db, lease_id=lease_id)

    if lease.tenant_id != tenant_id:
        raise LeaseNotFoundError()

    if lease.status in [LeaseStatus.TERMINATED, LeaseStatus.PENDING_TERMINATION, LeaseStatus.EXPIRED]:
        raise InvalidLeaseActionError(status=lease.status)

    return crud_lease.request_terminate_lease(db, db_lease=lease)

def verify_tenant_owns_lease(lease: Lease, tenant_id: int):
    return lease.tenant_id == tenant_id