"""
Module providing tenant-related business logic.

This module contains services for managing tenants and their profiles.
"""

from sqlalchemy.orm import Session, joinedload

from app.crud.invite import crud_invite
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole, InviteStatus, TenantStatus
from app.core.exceptions import (
    UserAlreadyExistError, LodgeNotFoundError, TenantProfileNotFoundError,
    InviteNotFoundError, InvalidInvitation, InvalidActionError,
    RentAmtExceededError, InvalidLeaseActionError, RoomNotFoundError
)
from app.core.security import get_password_hash
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.invitation import Invite
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate, TenantStatusUpdate, TenantApprovalCreate
from app.schemas.user import UserInternal
from app.services import lodge_service, room_service
from app.services.payment_service import can_add_payment
from app.crud.lease import crud_lease


def sign_up_tenant(
        db: Session,
        tenant_in: TenantProfileCreate,
):
    """
    Sign up a new tenant.

    Args:
        db (Session): The database session.
        tenant_in (TenantProfileCreate): The tenant profile creation data.

    Returns:
        TenantProfile: The newly created tenant profile.
    """
    invite_record = crud_invite.get_invite_record_by_id(db, invite_id=tenant_in.invite_id)
    
    if not invite_record:
        raise InviteNotFoundError(invite_id=tenant_in.invite_id)

    if invite_record.is_expired:
        raise InvalidInvitation(invite_status=InviteStatus.EXPIRED)

    if invite_record.status != InviteStatus.SENT:
        raise InvalidInvitation(invite_status=invite_record.status)

    if crud_user.get_user_by_email(db, email=tenant_in.user_info.email):
        raise UserAlreadyExistError(email=tenant_in.user_info.email)

    hashed = get_password_hash(tenant_in.user_info.password)

    base_user_data = UserInternal(
        first_name=tenant_in.user_info.first_name,
        last_name=tenant_in.user_info.last_name,
        phone_no=tenant_in.user_info.phone_no,
        email=tenant_in.user_info.email,
        hashed_password=hashed,
        role=UserRole.TENANT
    )

    return crud_tenant.create_tenant(db, tenant_in=tenant_in, internal_user=base_user_data,
                                     db_invite=invite_record)


def fetch_lodge_tenants(
        db: Session,
        lodge_id: int,
        landlord_user: User,
        skip: int ,
        limit: int,
        status: TenantStatus|None
):
    """
    Fetch all tenants for a specific lodge.

    Args:
        status: The status of the tenants to filter by. Defaults to None
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_user (User): The landlord user requesting the data.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        List[TenantProfile]: A list of tenant profiles.
    """
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_user.id)
    tenants = crud_tenant.get_tenants(db, lodge_id=lodge_id, skip=skip, max_limit=limit, status=status)
    return tenants


def update_tenant_profile(
        db: Session,
        base_user: User,
        update_data: TenantProfileUpdate
):
    """
    Update a tenant profile.

    Args:
        db (Session): The database session.
        base_user (User): The user associated with the tenant.
        update_data (TenantProfileUpdate): The updated tenant profile data.

    Returns:
        TenantProfile: The updated tenant profile.
    """

    tenant_user = base_user.tenant_profile

    return crud_tenant.update_tenant(db, update_data=update_data, tenant_user=tenant_user, base_user=base_user)


def fetch_tenant(
        current_user: User
):
    """
    Fetch the tenant profile of the current user.

    Args:
        current_user (User): The current user.

    Returns:
        TenantProfile: The tenant profile.
    """
    tenant_profile = current_user.tenant_profile

    if not tenant_profile:
        raise  TenantProfileNotFoundError()

    return tenant_profile


def fetch_tenant_by_landlord(
        db: Session,
        tenant_id: int,
        current_user: User
):
    """
    Fetch a tenant's profile by a landlord.

    Args:
        db (Session): The database session.
        tenant_id (int): The ID of the tenant.
        current_user (User): The landlord user.

    Returns:
        TenantProfile: The retrieved tenant profile.
    """
    options = joinedload(TenantProfile.lodge)

    tenant = crud_tenant.get(db, tenant_id, options)

    if not tenant:
        raise TenantProfileNotFoundError()

    lodge = tenant.lodge

    if lodge.landlord_id != current_user.id:
        raise TenantProfileNotFoundError()

    return tenant


def approve_tenant_application(
        db: Session,
        tenant_id: int,
        landlord_user: User,
        approval_data: TenantApprovalCreate
) -> Lease:
    """
    Approve a tenant's onboarding application and atomically create a Lease + initial Payment.

    Args:
        db (Session): The database session.
        tenant_id (int): The ID of the tenant profile.
        landlord_user (User): The authenticated landlord.
        approval_data (TenantApprovalCreate): Explicit lease terms and upfront payment.

    Returns:
        Lease: The newly created lease.
    """
    options = [
        joinedload(TenantProfile.lodge),
        joinedload(TenantProfile.invite)
    ]
    tenant = crud_tenant.get(db, tenant_id, *options)

    if not tenant:
        raise TenantProfileNotFoundError()

    if tenant.lodge.landlord_id != landlord_user.id:
        raise TenantProfileNotFoundError()

    if tenant.status != TenantStatus.PENDING:
        raise InvalidActionError(error_name='Tenant Status', error_value=tenant.status.value)

    target_room_id = tenant.invite.room_id if tenant.invite else None
    if not target_room_id:
        raise RoomNotFoundError(detail="No room associated with this tenant application")

    room = room_service.verify_room_existence(db, landlord_id=landlord_user.id, room_id=target_room_id)

    active_lease = crud_lease.get_active_lease_for_room(db, room_id=room.id)
    if active_lease:
        raise InvalidLeaseActionError(lease_status=active_lease.computed_status)

    default_total_payments = 0
    if not can_add_payment(
        total_payments=default_total_payments,
        incoming_amt=approval_data.total_amt_paid,
        agreed_amt=approval_data.agreed_rent_amt
    ):
        raise RentAmtExceededError(
            attempted=approval_data.total_amt_paid,
            current_total=default_total_payments,
            agreed=approval_data.agreed_rent_amt
        )

    return crud_tenant.approve_and_create_lease(
        db,
        tenant=tenant,
        room_id=room.id,
        approval_data=approval_data
    )


def reject_tenant_application(
        db: Session,
        tenant_id: int,
        landlord_user: User
) -> TenantProfile:
    """
    Reject a tenant's onboarding application.

    Args:
        db (Session): The database session.
        tenant_id (int): The ID of the tenant profile.
        landlord_user (User): The authenticated landlord.

    Returns:
        TenantProfile: The updated tenant profile with REJECTED status.
    """
    options = joinedload(TenantProfile.lodge)
    tenant = crud_tenant.get(db, tenant_id, options)

    if not tenant:
        raise TenantProfileNotFoundError()

    if tenant.lodge.landlord_id != landlord_user.id:
        raise TenantProfileNotFoundError()

    if tenant.status != TenantStatus.PENDING:
        raise InvalidActionError(error_name='Tenant Status', error_value=tenant.status.value)

    return crud_tenant.reject_tenant(db, tenant=tenant)


def update_tenant_profile_status(db: Session, tenant_id: int, landlord_id: int, update_data: TenantStatusUpdate):
    options = joinedload(TenantProfile.lodge)
    tenant = crud_tenant.get(db, tenant_id, options)

    if not tenant:
        raise TenantProfileNotFoundError()

    if tenant.lodge.landlord_id != landlord_id:
        raise TenantProfileNotFoundError()

    if update_data.status == TenantStatus.PENDING:
        raise InvalidActionError(error_name='Tenant Status', error_value=update_data.status)

    return crud_tenant.update(db, update_data=update_data, db_obj=tenant)


