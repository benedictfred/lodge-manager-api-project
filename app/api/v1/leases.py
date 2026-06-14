"""
API routes for managing leases.

Provides endpoints for creating, retrieving, updating, and terminating leases for both landlords and tenants.
"""
from app.core.enums import LeaseStatus
from app.schemas import lease as schema_lease
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import lease_services

router = APIRouter()


@router.post('/', response_model=schema_lease.LeaseResponse)
def create_new_lease(

        lease_data: schema_lease.LeaseCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):
    """
    Create a new lease.

    Args:
        lease_data (schema_lease.LeaseCreate): The lease data to create.
        db (Session): The database session.
        landlord_user (User): The authenticated landlord user.

    Returns:
        schema_lease.LeaseResponse: The created lease.
    """

    return lease_services.create_new_lease(
        db,
        lease_data=lease_data,
        landlord_user=landlord_user
    )



@router.get('/{lodge_id}', response_model=List[schema_lease.LeaseResponse])
def get_leases_for_landlord(
        lodge_id: int,
        room_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):
    """
    Get all leases for a specific lodge owned by the landlord.

    Args:
        lodge_id (int): The ID of the lodge.
        room_id (Optional[int]): Filter by room ID.
        tenant_id (Optional[int]): Filter by tenant ID.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.
        status (Optional[LeaseStatus]): Filter by lease status.
        db (Session): The database session.
        current_user (User): The authenticated landlord user.

    Returns:
        List[schema_lease.LeaseResponse]: A list of leases.
    """


    return lease_services.get_filtered_landlord_leases(
        db,
        landlord_id=current_user.id,
        lodge_id=lodge_id,
        tenant_id=tenant_id,
        room_id=room_id,
        skip=skip,
        max_limit=limit,
        status=status

        )



@router.get('/tenant/me', response_model=List[schema_lease.LeaseResponse])
def get_tenant_leases(
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None,
        db: Session = Depends(get_db),
        tenant_user: User = Depends(get_tenant_user)
):
    """
    Get all leases for the currently authenticated tenant.

    Args:
        skip (Optional[int]): Number of records to skip.
        max_limit (Optional[int]): Maximum number of records to return.
        status (Optional[LeaseStatus]): Filter by lease status.
        db (Session): The database session.
        tenant_user (User): The authenticated tenant user.

    Returns:
        List[schema_lease.LeaseResponse]: A list of the tenant's leases.
    """
    #leases must belong to the tenant
    #leases can be filtered by active

    return lease_services.get_filtered_leases_tenant(
            db,
            tenant_profile=tenant_user.tenant_profile,
            skip=skip,
            max_limit=max_limit,
            status=status

        )



@router.patch('/{lease_id}', response_model=schema_lease.LeaseResponse)
def update_lease_by_id(
        lease_id: int,
        lease_data: schema_lease.LeaseUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):
    """
    Update details of an existing lease.

    Args:
        lease_id (int): The ID of the lease to update.
        lease_data (schema_lease.LeaseUpdate): The updated lease data.
        db (Session): The database session.
        current_user (User): The authenticated landlord user.

    Returns:
        schema_lease.LeaseResponse: The updated lease.
    """
    
    return lease_services.update_lease_details(db, lease_id=lease_id, update_data=lease_data, landlord_id=current_user.id)


@router.patch('/terminate/{lease_id}', response_model=schema_lease.LeaseResponse)
def terminate_lease_by_id(
        lease_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):
    """
    Terminate a lease by its ID. Only landlords can perform this action.

    Args:
        lease_id (int): The ID of the lease to terminate.
        db (Session): The database session.
        current_user (User): The authenticated landlord user.

    Returns:
        schema_lease.LeaseResponse: The terminated lease.
    """
    #the landlord can only terminate leases in his specific lodge
    #the lease must exist

    return lease_services.terminate_lease(db, lease_id=lease_id, landlord_id=current_user.id
                                                                              )


@router.patch('/me/terminate/{lease_id}', response_model=schema_lease.LeaseResponse)
def request_lease_termination(
        lease_id: int,
        db: Session = Depends(get_db),
        current_tenant: User = Depends(get_tenant_user)
):
    """
    Request the termination of an active lease by a tenant.

    Args:
        lease_id (int): The ID of the lease to request termination for.
        db (Session): The database session.
        current_tenant (User): The authenticated tenant user.

    Returns:
        schema_lease.LeaseResponse: The lease with a pending termination request.
    """
    #tenant can have multiple active leases
    #tenant must be able to request termination of only his selected active lease
    return lease_services.appeal_for_lease_termination(
        db,
        lease_id=lease_id,
        tenant_id = current_tenant.tenant_profile.id
    )



