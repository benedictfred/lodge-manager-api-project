from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import lodge as lodge_schema
from app.api.deps import get_current_user
from app.models.user import User
from app.crud import lodge as crud_lodge


router = APIRouter()

@router.post('/register', response_model=lodge_schema.LodgeResponse)
def register_lodge(
        lodge_in: lodge_schema.LodgeCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    lodge_exist = crud_lodge.get_lodge_by_name_and_landlord(db, landlord_id=current_user.id, lodge_name=lodge_in.name)

    if lodge_exist:
        raise HTTPException(
            status_code=400,
            detail=f'You have a lodge with that name'
        )
    return crud_lodge.create_lodge(db, lodge_data=lodge_in, landlord_id=current_user.id)


@router.get('/{lodge_id}', response_model=lodge_schema.LodgeResponse)
def get_lodge_by_id(lodge_id: int):
    pass


@router.get('/')
def get_lodges_by_landlord():
    pass


@router.patch('/{lease_id}')
def update_lodge_details(lease_id: int):
    pass


