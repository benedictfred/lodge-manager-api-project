from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user as schema_user
from app.crud import user as crud_user
from app.core.security import verify_password_hash, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post('/register', response_model=schema_user.UserResponse)
def sign_up_user(
        user_data: schema_user.UserCreate,
        db: Session = Depends(get_db)
):
    user_exist = crud_user.get_user_by_email(db=db, email=user_data.email.lower())

    if user_exist:
        raise HTTPException(
            status_code=400,
            detail=f'User with email: {user_data.email} already exists'
        )

    return crud_user.create_user(db=db, user_data=user_data)


@router.post('/login')
def login_user(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid email or password'
    )
    user = crud_user.get_user_by_email(db=db, email=form_data.username.lower())


    if not user :
        raise unauthorized_exception

    verified_password = verify_password_hash(
        plain_password=form_data.password,
        hashed_password=user.hashed_password

    )

    if not verified_password:
        raise unauthorized_exception


    access_token = create_access_token(
        subject=user.id
    )


    return{
        'access_token': access_token,
        'token_type': 'bearer'
    }
