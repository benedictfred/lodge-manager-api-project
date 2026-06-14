"""
API routes for managing tenants.

Provides endpoints for updating tenant profiles and fetching tenant details.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import tenantprofile as schema_tenant
from app.crud.tenantprofile import crud_tenant
from app.api.deps import get_db, get_current_user, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import tenant_services

router = APIRouter()




@router.patch('/profiles/me', response_model=schema_tenant.TenantProfileResponse)
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



@router.get('/profile', response_model=schema_tenant.TenantProfileResponse)
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




@router.get('/profile/{tenant_id}', response_model=schema_tenant.TenantProfileResponse)
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
@router.delete('/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
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
