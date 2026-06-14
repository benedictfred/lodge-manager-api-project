"""
Module providing tenant-related business logic.

This module contains services for managing tenants and their profiles.
"""
from typing import cast

from sqlalchemy.orm import Session

from app.crud.lodge import crud_lodge
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError, LodgeNotFoundError, UserNotFoundError
from app.core.security import get_password_hash
from app.models.lodge import Lodge
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate
from app.schemas.user import UserInternal
from app.services import lodge_service
from app.services.lodge_service import is_landlord, is_tenant


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
    if not crud_lodge.get(db, item_id=tenant_in.tenant_info.lodge_id):
        raise LodgeNotFoundError()

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

    return crud_tenant.create_tenant(db, tenant_in=tenant_in, internal_user=base_user_data)


def fetch_lodge_tenants(
        db: Session,
        lodge_id: int,
        landlord_user: User,
        skip: int,
        limit: int
):
    """
    Fetch all tenants for a specific lodge.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_user (User): The landlord user requesting the data.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        List[TenantProfile]: A list of tenant profiles.
    """
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_user.id)
    tenants = crud_tenant.get_tenants(db, lodge_id=lodge_id, skip=skip, max_limit=limit)
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
        raise  UserNotFoundError()

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
    tenant = crud_tenant.get(db, item_id=tenant_id)

    if not tenant:
        raise UserNotFoundError()

    lodge = tenant.lodge

    if lodge.landlord_id != current_user.id:
        raise UserNotFoundError()

    return tenant
