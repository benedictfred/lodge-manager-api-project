# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
#
# from app.schemas import  tenant as schema_tenant
# from app.crud import tenant as crud_tenant
# from typing import List
# from app.api.deps import get_db, get_current_user
# from app.models.user import LandLord
#
#
# router = APIRouter()
#
# @router.get('/', response_model=List[schema_tenant.TenantResponse])
# def get_all_tenants(
#         skip: int = 0,
#         limit: int = 50,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     return crud_tenant.get_tenants(db=db, skip=skip, max_limit=limit)
#
#
# @router.post('/create-tenant', response_model=schema_tenant.TenantResponse)
# def create_new_tenant(
#         tenant_data : schema_tenant.TenantCreate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     tenant = crud_tenant.get_tenant_by_email(db=db, email=tenant_data.email)
#
#     if tenant:
#         raise HTTPException(
#             status_code=400,
#             detail=f'Tenant with email: {tenant_data.email} already exists'
#         )
#
#     return crud_tenant.create_tenant(db=db,tenant_data=tenant_data)
#
#
# @router.patch('/{tenant_id}')
# def update_tenant_by_id(
#         tenant_id: int,
#         tenant_data : schema_tenant.TenantUpdate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)
#
#     if not tenant:
#         raise HTTPException(
#             status_code=404,
#             detail= 'Tenant not found'
#         )
#     return crud_tenant.update_tenant(db=db, db_tenant=tenant, tenant_data=tenant_data)
#
#
# @router.get('/{tenant_id}', response_model=schema_tenant.TenantResponse)
# def get_tenant_by_id(
#         tenant_id: int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)
#
#     if not tenant:
#         raise HTTPException(
#             status_code=404,
#             detail='Tenant not found'
#         )
#     return tenant
#
# @router.delete('/{tenant_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_tenant_by_id(
#         tenant_id: int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
#
#
# ):
#     tenant = crud_tenant.get_tenant(db=db, tenant_id=tenant_id)
#
#     if not tenant:
#         raise HTTPException(
#             status_code=404,
#             detail='Tenant not found'
#         )
#
#     crud_tenant.delete_tenant(db=db, db_tenant=tenant)
#
#
