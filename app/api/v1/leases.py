from app.core.enums import LeaseStatus
from app.core.exceptions import UserNotFoundError, RoomNotFoundError, ActiveLeaseFoundError, LodgeNotFoundError
from app.crud.room import crud_room
from app.crud.tenantprofile import crud_tenant
from app.crud import lease as crud_lease
from app.models.room import RoomStatus
from app.schemas import lease as schema_lease
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
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
    try:
        return lease_services.create_new_lease(
            db,
            lease_data=lease_data,
            landlord_user=landlord_user
        )
    except RoomNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except ActiveLeaseFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get('/{lodge_id}', response_model=List[schema_lease.LeaseResponse])
def get_leases_for_landlord(
        lodge_id: int,
        room_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):
    try:

        return lease_services.filter_leases_for_landlord(
            db,
            landlord_id=current_user.id,
            lodge_id=lodge_id,
            tenant_id=tenant_id,
            room_id=room_id,
            skip=skip,
            max_limit=max_limit,
            status=status

            )
    except LodgeNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.get('/tenant/me')
def get_tenant_leases(
        skip: Optional[int] = None,
        max_limit: Optional[int] = None,
        status: Optional[LeaseStatus] = None,
        db: Session = Depends(get_db),
        tenant_user: User = Depends(get_tenant_user)
):
    #leases must belong to the tenant
    #leases can be filtered by active

    return lease_services.filter_leases(
            db,
            tenant_id=tenant_user.id,
            skip=skip,
            max_limit=max_limit,
            status=status

        )



# @router.get('/{lease_id}', response_model=schema_lease.LeaseResponse)
# def get_lease_land(
#         lease_id: int,
#         db: Session = Depends(get_db),
#         current_user:  = Depends(get_current_user)
# ):
#     lease = crud_lease.get_lease(db=db, lease_id=lease_id)
#
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return lease


# @router.patch('/{lease_id}', response_model=schema_lease.LeaseResponse)
# def update_lease_by_id(
#         lease_id: int,
#         lease_data: schema_lease.LeaseUpdate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     lease = crud_lease.get_lease(db=db, lease_id=lease_id)
#
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#
#         )
#     return crud_lease.update_lease(db=db, lease_data=lease_data, db_lease=lease)
#
#
# @router.patch('/terminate/{lease_id}', response_model=schema_lease.LeaseResponse)
# def terminate_lease_by_id(
#         lease_id: int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     lease = crud_lease.get_lease(db=db, lease_id=lease_id)
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return crud_lease.terminate_lease(db=db, db_lease=lease)
