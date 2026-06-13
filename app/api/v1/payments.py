from typing import Optional

from app.crud import payment as crud_payment
from app.crud import lease as crud_lease
from app.schemas import payment as schema_payment
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_landlord_user, get_tenant_user
from app.models.user import User
from app.services import payment_service

router = APIRouter()
#create a payment record endpoint by landlord in a lease
#

@router.post('/create-payment', response_model=schema_payment.PaymentResponse)
def create_payment(
        payment_data: schema_payment.PaymentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_landlord_user)
):

    #does the lease exist and belong in the lodge of the current landlord

    return payment_service.add_payment_record(
        db,
        current_landlord_id=current_user.id,
        payment_data=payment_data
    )


@router.get('/{lease_id}', response_model=List[schema_payment.PaymentResponse])
def list_lease_payments_for_landlord(
        lease_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    #only get payments that the landlord has access to....
    #use pagination while fetching the payment history

    return payment_service.fetch_payments_by_lease(
        db,
        lease_id= lease_id,
        skip=skip,
        limit=limit,
        landlord_id=current_user.id
    )

@router.get('/me/{lease_id}', response_model=List[schema_payment.PaymentResponse])
def list_tenant_payments(
        lease_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        db: Session = Depends(get_db),
        tenant_user: User = Depends(get_tenant_user)

):
    return payment_service.fetch_tenant_lease_payments(
        db,
        lease_id=lease_id,
        skip=skip,
        limit=limit,
        tenant_id = tenant_user.tenantprofile.id
    )



# @router.get('/{pay_id}', response_model=schema_payment.PaymentResponse)
# def get_payment_by_id(
#         pay_id : int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     lease = crud_payment.get_payment_by_id(db=db, pay_id=pay_id)
#     if not lease:
#         raise HTTPException(
#             status_code=404,
#             detail='Lease not Found'
#         )
#     return lease



