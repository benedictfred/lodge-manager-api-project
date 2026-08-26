"""
API routes for managing tenants.

Provides endpoints for updating tenant profiles and fetching tenant details.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import tenantprofile as schema_tenant
from app.schemas.error import ErrorResponseSchema
from app.crud.tenantprofile import crud_tenant
from app.api.deps import get_db, get_current_user, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import tenant_services

router = APIRouter()




@router.patch(
    '/profiles/me',
    response_model=schema_tenant.TenantProfileResponse,
    summary="Update my tenant profile",
    description=(
        "Updates the authenticated tenant's profile information "
        "such as emergency contacts and student details."
    ),
    response_description="Updated tenant profile",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only tenant accounts can perform this action"},
    },
)
def update_tenant_profile(
        tenant_data: schema_tenant.TenantProfileUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_tenant_user)
):
    """
    Update the profile of the currently authenticated tenant.

    Args:
        tenant_data (schema_tenant.TenantProfileUpdate): The updated tenant profile data.
        db (Session): The database session.
        current_user (User): The authenticated tenant user.

    Returns:
        schema_tenant.TenantProfileResponse: The updated tenant profile.
    """

    return tenant_services.update_tenant_profile(
        db=db,
        update_data=tenant_data,
        base_user=current_user,
    )



@router.get(
    '/profile',
    response_model=schema_tenant.TenantProfileResponse,
    summary="Get my tenant profile",
    description=(
        "Retrieves the full profile of the currently authenticated tenant."
    ),
    response_description="Tenant profile details",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only tenant accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Tenant profile not found for the authenticated user"},
    },
)
def get_tenant_by_id(
        current_user=Depends(get_tenant_user)
):
    """
    Retrieve the profile of the currently authenticated tenant.

    Args:
        current_user (User): The authenticated tenant user.

    Returns:
        schema_tenant.TenantProfileResponse: The tenant profile.
    """
    return tenant_services.fetch_tenant(current_user=current_user)




@router.get(
    '/profile/{tenant_id}',
    response_model=schema_tenant.TenantProfileResponse,
    summary="Get tenant profile by ID",
    description=(
        "Retrieves a specific tenant's profile. "
        "The tenant must belong to a lodge owned by the authenticated landlord."
    ),
    response_description="Tenant profile details",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Tenant does not exist or does not belong to a lodge owned by this landlord"},
    },
)
def get_tenant_by_landlord(
        tenant_id: int,
        db: Session = Depends(get_db),
        current_user: User =Depends(get_landlord_user)

):
    """
    Retrieve the profile of a specific tenant by the landlord.

    Args:
        tenant_id (int): The ID of the tenant.
        db (Session): The database session.
        current_user (User): The authenticated landlord user.

    Returns:
        schema_tenant.TenantProfileResponse: The tenant profile.
    """

    return tenant_services.fetch_tenant_by_landlord(db, tenant_id=tenant_id, current_user=current_user)



#TODO: finish the endpoint later
@router.delete(
    '/{tenant_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tenant",
    description=(
        "Deletes a tenant profile. This endpoint is under construction."
    ),
    response_description="No content on successful deletion",
    responses={
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
    },
)
def delete_tenant_by_id(
        tenant_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    """
    Delete a specific tenant by their ID.

    Args:
        tenant_id (int): The ID of the tenant to delete.
        db (Session): The database session.
        current_user (User): The authenticated user.

    Raises:
        HTTPException: If the tenant is not found.
    """
    #is logged user a tenant..
    #
    tenant = crud_tenant

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )

    crud_tenant.delete_tenant(db=db, db_tenant=tenant)

from app.schemas import lease as schema_lease




@router.post(
    '/{tenant_id}/approve',
    response_model=schema_lease.LeaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Approve tenant onboarding application",
    description=(
        "Approves a tenant's onboarding application and atomically generates "
        "their lease and first upfront payment, setting the room status to OCCUPIED."
    ),
    response_description="Created lease agreement",
    responses={
        400: {"model": ErrorResponseSchema, "description": "Invalid dates, payment exceeds rent, or room not available"},
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Tenant or room not found"},
    },
)
def approve_tenant(
        tenant_id: int,
        approval_data: schema_tenant.TenantApprovalCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    return tenant_services.approve_invited_tenant_application(
        db=db,
        tenant_id=tenant_id,
        landlord_user=landlord_user,
        approval_data=approval_data
    )


@router.post(
    '/{tenant_id}/reject',
    response_model=schema_tenant.TenantProfileResponse,
    summary="Reject tenant onboarding application",
    description="Rejects a tenant's onboarding application, leaving the room vacant.",
    response_description="Updated tenant profile with REJECTED status",
    responses={
        400: {"model": ErrorResponseSchema, "description": "Tenant is not in pending status"},
        401: {"model": ErrorResponseSchema, "description": "Missing, invalid, or expired access token"},
        403: {"model": ErrorResponseSchema, "description": "Only landlord accounts can perform this action"},
        404: {"model": ErrorResponseSchema, "description": "Tenant does not exist or does not belong to this landlord"},
    },
)
def reject_tenant(
        tenant_id: int,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    return tenant_services.reject_tenant_application(
        db=db,
        tenant_id=tenant_id,
        landlord_user=landlord_user
    )