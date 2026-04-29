# from app.crud import payment as crud_payment
# from app.crud import lease as crud_lease
# from app.schemas import payment as schema_payment
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.api.deps import get_db, get_current_user
# from app.models.user import LandLord
#
#
# router = APIRouter()
#
#
# @router.post('/create-payment', response_model=schema_payment.PaymentResponse)
# def create_payment(
#         payment_data: schema_payment.PaymentCreate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#
#     lease = crud_lease.get_lease(db=db, lease_id=payment_data.lease_id)
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail= 'Lease not found'
#         )
#
#     return crud_payment.create_payment(db=db, pay_data=payment_data)
#
#
# @router.get('/history', response_model=List[schema_payment.PaymentResponse])
# def get_payments(
#         skip: int = 0,
#         limit: int = 20,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     return crud_payment.get_payments(db=db, skip=skip, limit=limit)
#
#
# @router.get('/{pay_id}', response_model=schema_payment.PaymentResponse)
# def get_payment_by_id(
#         pay_id : int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     lease = crud_payment.get_payment_by_id(db=db, pay_id=pay_id)
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return lease
#
#
#
# @router.get('/history/{lease_id}', response_model=List[schema_payment.PaymentResponse])
# def get_payments_history_by_lease_id(
#         lease_id: int,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
# ):
#     return crud_payment.get_payments_by_lease_id(db=db, lease_id=lease_id)
#
#
# @router.patch('/{pay_id}', response_model=schema_payment.PaymentResponse)
# def update_payment_by_id(
#         pay_id: int,
#         update_data: schema_payment.PaymentUpdate,
#         db: Session = Depends(get_db),
#         current_user: LandLord = Depends(get_current_user)
#
# ):
#     payment = crud_payment.get_payment_by_id(db=db, pay_id=pay_id)
#
#     if not payment:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return crud_payment.update_payment(db=db, db_payment=payment, pay_data=update_data)
#
