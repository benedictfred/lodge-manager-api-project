from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import LodgeNotFoundError
from app.services import tenant_services
from app.schemas import tenantprofile as schema_tenant
from app.crud import tenantprofile as crud_tenant
from typing import List
from app.api.deps import get_db, get_current_user, get_landlord_user
from app.models.user import User

router = APIRouter()


@router.patch('/{tenant_id}')
def update_tenant_profile(
        lodge_id: int,
        tenant_id: int,
        tenant_data: schema_tenant.TenantProfileUpdate,
        db: Session = Depends(get_db),
        tenant_user=Depends(get_current_user)
):
    #only tenants shd be able to update their info
    #the tenants must belong to a specific lodge

    tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )
    return crud_tenant.update_tenant(db=db, db_tenant=tenant, tenant_data=tenant_data)


@router.get('/{tenant_id}', response_model=schema_tenant.TenantProfileResponse)
def get_tenant_by_id(
        tenant_id: int,
        db: Session = Depends(get_db),
        tenant_user=Depends(get_current_user)
):
    tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )
    return tenant


@router.delete('/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_by_id(
        tenant_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail='Tenant not found'
        )

    crud_tenant.delete_tenant(db=db, db_tenant=tenant)

