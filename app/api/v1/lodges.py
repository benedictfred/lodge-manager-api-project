from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_landlord_user
from app.schemas import lodge as lodge_schema
from app.schemas import tenantprofile as schema_tenant
from app.models.user import User
from app.crud.lodge import crud_lodge
from app.services import lodge_service, tenant_services

router = APIRouter()

@router.post('/register', response_model=lodge_schema.LodgeResponse)
def register_lodge(
        lodge_in: lodge_schema.LodgeCreate,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)

):

    return lodge_service.create_new_lodge_for_landlord(
        db=db,
        landlord_id=landlord_user.id,
        lodge_in=lodge_in
    )



@router.get('/{lodge_id}', response_model=lodge_schema.LodgeResponse)
def get_lodge_by_id(
        lodge_id: int,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):

    return lodge_service.verify_lodge_ownership(db=db, lodge_id=lodge_id, landlord_id=landlord_user.id)


@router.get('/', response_model=List[lodge_schema.LodgeResponse])
def get_lodges_by_landlord(
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user),
        skip: int = 0,
        limit: int = 50
):

    return crud_lodge.get_lodges_by_owner(db=db, landlord_id=landlord_user.id, skip=skip, limit=limit)


@router.get('/{lodge_id}/tenants', response_model=List[schema_tenant.TenantProfileResponse])
def get_lodge_tenants(
        lodge_id: int,
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(get_db),
        landlord_user: User = Depends(get_landlord_user)
):

    return tenant_services.fetch_lodge_tenants(
        db,
        lodge_id=lodge_id,
        landlord_user=landlord_user,
        skip=skip,
        limit=limit
    )


@router.patch('/{lodge_id}', response_model=lodge_schema.LodgeResponse)
def update_lodge_details(
        lodge_id: int,
        update_data: lodge_schema.LodgeUpdate,
        landlord_user: User = Depends(get_landlord_user),
        db: Session = Depends(get_db)
):
    return lodge_service.update_landlord_lodge(
        db=db, lodge_id=lodge_id,
        landlord_id=landlord_user.id,
        update_data=update_data
    )






