# from app.crud import room as crud_room
# from app.crud import tenant as crud_tenant
# from app.crud import lease as crud_lease
# from app.models.room import RoomStatus
# from app.schemas import lease as schema_lease
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.api.deps import get_db,get_current_user
# from app.models.user import LandLord
#
# router = APIRouter()
#
#
# @router.get('/', response_model=List[schema_lease.LeaseResponse])
# def get_leases(
#         skip: int = 0,
#         max_limit: int = 50,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     return crud_lease.get_leases(db=db, skip=skip, max_limit=max_limit)
#
#
# @router.get('/{lease_id}', response_model=schema_lease.LeaseResponse)
# def get_lease_by_id(
#         lease_id: int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     lease = crud_lease.get_lease(db=db, lease_id=lease_id)
#
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return lease
#
#
#
#
# @router.post('/create-lease', response_model=schema_lease.LeaseResponse)
# def create_lease(
#         lease_data: schema_lease.LeaseCreate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     room = crud_room.get_room(db=db, room_id=lease_data.room_id)
#     if not room:
#         raise HTTPException(
#             status_code=404,
#             detail='Room not Found'
#         )
#
#     tenant = crud_tenant.get_tenant(db=db, tenant_id=lease_data.tenant_id)
#
#     if not tenant:
#         raise HTTPException(
#             status_code=404,
#             detail='Tenant not Found'
#         )
#
#     if room.status == RoomStatus.OCCUPIED:
#         raise HTTPException(
#             status_code=400,
#             detail='The Room is Occupied'
#         )
#
#     active_lease = crud_lease.get_active_lease_by_tenant(db=db, tenant=tenant)
#     if active_lease:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Tenant is already in an active lease (Lease ID: {active_lease.id}) for Room ID: {active_lease.room_id}"
#         )
#
#     return crud_lease.create_lease(db=db, lease_data=lease_data, room=room)
#
#
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