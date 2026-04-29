from typing import List

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'You have a lodge with that name'
        )
    return crud_lodge.create_lodge(db, lodge_data=lodge_in, landlord_id=current_user.id)


@router.get('/{lodge_id}', response_model=lodge_schema.LodgeResponse)
def get_lodge_by_id(
        lodge_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    lodge = crud_lodge.get_lodge(db=db, lodge_id=lodge_id, landlord_id=current_user.id)
    if not lodge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Lodge not found'
        )
    return lodge

@router.get('/', response_model=List[lodge_schema.LodgeResponse])
def get_lodges_by_landlord(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 50
):
    lodges = crud_lodge.get_lodges(db=db, landlord_id=current_user.id, skip=skip, limit=limit)
    if not lodges:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No lodges found'
        )
    return lodges


@router.patch('/{lodge_id}')
def update_lodge_details(
        lodge_id: int,
        update_data: lodge_schema.LodgeUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    lodge = crud_lodge.get_lodge(db=db, lodge_id=lodge_id, landlord_id=current_user.id)

    if not lodge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Lodge not found.')
    return crud_lodge.update_lodge(db, db_lodge=lodge, lodge_data=update_data)


