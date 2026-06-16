"""
Module providing lease-related business logic.

This module contains services for managing leases.
"""
from typing import Optional
from app.core.enums import LeaseStatus
from app.crud.tenantprofile import crud_tenant
from app.models.lease import Lease
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.lease import LeaseCreate, LeaseUpdate
from app.services import lodge_service, room_service
from app.crud.lease import crud_lease
from app.core.exceptions import (RoomNotFoundError, UserNotFoundError,
                                 LeaseNotFoundError, InvalidLeaseActionError)


def create_new_lease(
        db: Session,
        lease_data: LeaseCreate,
        landlord_user: User
):
    """
    Create a new lease.

    Args:
        db (Session): The database session.
        lease_data (LeaseCreate): The lease creation data.
        landlord_user (User): The landlord user creating the lease.

    Returns:
        Lease: The newly created lease.
    """
    room = room_service.verify_room_existence(db, landlord_id=landlord_user.id, room_id=lease_data.room_id)

    tenant = crud_tenant.get(db, item_id=lease_data.tenant_id)

    if not tenant or tenant.lodge.landlord_id != landlord_user.id:
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
    """
    Get filtered leases for a landlord.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_id (int): The ID of the landlord.
        tenant_id (Optional[int]): Filter by tenant ID.
        room_id (Optional[int]): Filter by room ID.
        skip (Optional[int]): Number of records to skip.
        max_limit (Optional[int]): Maximum number of records to return.
        status (Optional[LeaseStatus]): Filter by lease status.

    Returns:
        list[Lease]: A list of filtered leases.
    """
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    return filter_leases(
        db,
        lodge_id=lodge_id,
        tenant_id=tenant_id,
        room_id=room_id,
        skip=skip,
        max_limit=max_limit,
        status=status
    )


def get_filtered_leases_tenant(
        db: Session,
        tenant_profile: TenantProfile,
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None
):
    """
    Get filtered leases for a specific tenant.

    Args:
        db (Session): The database session.
        tenant_profile (TenantProfile): The tenant's profile.
        skip (Optional[int]): Number of records to skip.
        max_limit (Optional[int]): Maximum number of records to return.
        status (Optional[LeaseStatus]): Filter by lease status.

    Returns:
        list[Lease]: A list of filtered leases.
    """

    if not tenant_profile:
        raise UserNotFoundError()

    lodge = tenant_profile.lodge

    return filter_leases(
        db,
        tenant_id=tenant_profile.id,
        skip=skip,
        max_limit=max_limit,
        status=status,
        lodge_id=lodge.id
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
    """
    Filter leases based on provided criteria.

    Args:
        db (Session): The database session.
        lodge_id (Optional[int]): Filter by lodge ID.
        tenant_id (Optional[int]): Filter by tenant ID.
        room_id (Optional[int]): Filter by room ID.
        skip (Optional[int]): Number of records to skip.
        max_limit (Optional[int]): Maximum number of records to return.
        status (Optional[LeaseStatus]): Filter by lease status.

    Returns:
        list[Lease]: A list of filtered leases.
    """

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
    """
    Verify if a lease can be terminated.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease.

    Returns:
        Lease: The verified lease.
    """
    lease = crud_lease.get(db, item_id=lease_id)

    if not lease:
        raise LeaseNotFoundError()

    # don't terminate a lease if it has already been terminated
    if lease.status == LeaseStatus.TERMINATED:
        raise InvalidLeaseActionError(status=lease.status)

    return lease


def terminate_lease(
        db: Session,
        lease_id: int,
        landlord_id: int,
):
    """
    Terminate a specific lease.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease to terminate.
        landlord_id (int): The ID of the landlord.

    Returns:
        Lease: The terminated lease.
    """

    lease = verify_lease_to_terminate(db, lease_id=lease_id)

    room = lease.room

    if room.lodge.landlord_id != landlord_id:
        raise RoomNotFoundError()

    return crud_lease.lease_terminate(db, db_lease=lease)


def update_lease_details(
        db: Session,
        lease_id: int,
        update_data: LeaseUpdate,
        landlord_id: int,
):
    """
    Update details of a specific lease.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease.
        update_data (LeaseUpdate): The data to update.
        landlord_id (int): The ID of the landlord.

    Returns:
        Lease: The updated lease.
    """
    lease = crud_lease.get(db, item_id=lease_id)

    if not lease:
        return LeaseNotFoundError()

    if lease.room.lodge.landlord_id != landlord_id:
        return LeaseNotFoundError()

    return crud_lease.update_lease(db, db_lease=lease, lease_data=update_data)


def appeal_for_lease_termination(
        db: Session,
        lease_id: int,
        tenant_id: int
):
    """
    Appeal to terminate a lease by a tenant.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease.
        tenant_id (int): The ID of the tenant.

    Returns:
        Lease: The lease with termination requested status.
    """

    lease = verify_lease_to_terminate(db, lease_id=lease_id)

    if not verify_tenant_owns_lease(lease=lease, tenant_id=tenant_id):
        raise LeaseNotFoundError()

    if lease.status == LeaseStatus.PENDING_TERMINATION:
        raise InvalidLeaseActionError(status=lease.status)

    return crud_lease.request_terminate_lease(db, db_lease=lease)


def verify_tenant_owns_lease(lease: Lease, tenant_id: int):
    """
    Verify if a tenant owns a specific lease.

    Args:
        lease (Lease): The lease object.
        tenant_id (int): The ID of the tenant.

    Returns:
        bool: True if the tenant owns the lease, False otherwise.
    """
    return lease.tenant_id == tenant_id
