from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user as schema_user
from app.schemas import tenantprofile as schema_tenant

from app.services import user_service
from app.services.tenant_services import sign_up_tenant
from app.core.exceptions import UserAlreadyExistError

router = APIRouter()


@router.post('/register/landlord', response_model=schema_user.UserResponse, status_code=201)
def register_landlord(
        landlord_in: schema_user.UserCreate,
        db: Session = Depends(get_db)
):
    try:
        return user_service.sign_up_landlord(db=db, landlord_data=landlord_in)
    except UserAlreadyExistError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post('/register/tenant', response_model=schema_tenant.TenantProfileResponse, status_code=201)
def register_tenant(
        tenant_in: schema_tenant.TenantProfileCreate,
        db: Session = Depends(get_db)
):

    return sign_up_tenant(db=db, tenant_in=tenant_in)




@router.post('/login', response_model=schema_user.Token)
def login_user(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    return user_service.login_authenticated_user(db, email=form_data.username.lower(), password=form_data.password)
