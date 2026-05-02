from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user as schema_user
from app.core.security import  create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.core.enums import UserRole
from app.services.user_service import sign_up_user, authenticate_user
from app.core.exceptions import UserAlreadyExistError

router = APIRouter()


@router.post('/register/landlord', response_model=schema_user.UserResponse, status_code=201)
def register_landlord(
        user_data: schema_user.UserCreate,
        db: Session = Depends(get_db)
):
    try:
        return  sign_up_user(user_data=user_data, db=db)
    except UserAlreadyExistError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post('/register/tenant', response_model=schema_user.UserResponse, status_code=201)
def register_tenant(
        user_data: schema_user.UserCreate,
        db: Session = Depends(get_db)
):
    try:
        return sign_up_user(user_data=user_data, db=db, role=UserRole.TENANT)

    except UserAlreadyExistError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post('/login')
def login_user(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid email or password'
    )
    authenticated_user = authenticate_user(db, email=form_data.username.lower(), password=form_data.password)


    if not authenticated_user :
        raise unauthorized_exception


    access_token = create_access_token(
        subject=str(authenticated_user.id)
    )


    return{
        'access_token': access_token,
        'token_type': 'bearer'
    }
