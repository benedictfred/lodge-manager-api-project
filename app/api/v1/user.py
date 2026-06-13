from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user as schema_user
from app.schemas import tenantprofile as schema_tenant
from app.services import user_service, tenant_services

router = APIRouter()


@router.post('/register/landlord', response_model=schema_user.UserResponse, status_code=201)
def register_landlord(
        landlord_in: schema_user.UserCreate,
        db: Session = Depends(get_db)
):

    return user_service.sign_up_landlord(db=db, landlord_data=landlord_in)


@router.post('/register/tenant', response_model=schema_tenant.TenantProfileResponse, status_code=201)
def register_tenant(
        tenant_in: schema_tenant.TenantProfileCreate,
        db: Session = Depends(get_db)
):

    return tenant_services.sign_up_tenant(db=db, tenant_in=tenant_in)




@router.post('/login', response_model=schema_user.Token)
def login_user(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    return user_service.login_authenticated_user(db, email=form_data.username.lower(), password=form_data.password)
