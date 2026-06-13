from app.core.enums import LeaseStatus
from app.core.exceptions import LeaseNotFoundError, RoomNotFoundError, InvalidLeaseActionError, RentAmtExceededError
from app.crud.payment import crud_payment
from app.crud.lease import crud_lease
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.payment import PaymentCreate
from app.services import lodge_service
from app.services.lease_services import verify_tenant_owns_lease


def can_add_payment(total_payments: int, incoming_amt: int, agreed_amt: int) -> bool:
    return total_payments + incoming_amt <= agreed_amt


def add_payment_record(
        db: Session,
        current_landlord_id: int,
        payment_data: PaymentCreate
):
    #use the lease id in the payment data to find the lease
    #verify that the landlord owns the lodge the lease is in
    #if lease exist create a payment record with that lease id...
    #you can't add payment record to a lease whose agreed_rent_amt is equal to the aggregate of the payments made for that lease
    #can't add payment for leases that are not active

    lease = crud_lease.get(db, item_id=payment_data.lease_id)

    if not lease:
        raise LeaseNotFoundError()

    room = lease.room

    if not lodge_service.landlord_owns_room_lodge(room=room, landlord_id=current_landlord_id):
        raise RoomNotFoundError()

    if lease.status != LeaseStatus.ACTIVE:
        raise InvalidLeaseActionError(status=lease.status)

    total_payments = crud_payment.get_payments_aggregate_by_lease_id(db, lease_id=lease.id) or 0

    if not can_add_payment(total_payments=total_payments, incoming_amt=payment_data.amount_paid,
                           agreed_amt=lease.agreed_rent_amt):
        print(f'total_payment: {total_payments} ')
        raise RentAmtExceededError(
            attempted=payment_data.amount_paid,
            current_total=total_payments,
            agreed=lease.agreed_rent_amt
        )

    return crud_payment.create(db, obj_in=payment_data)


def fetch_payments_by_lease(
        db: Session,
        lease_id: int,
        landlord_id: int,
        skip: Optional[int],
        limit: Optional[int]
):
    lease = crud_lease.get(db, item_id=lease_id)

    if not lease:
        raise LeaseNotFoundError()

    room = lease.room

    if not lodge_service.landlord_owns_room_lodge(room=room, landlord_id=landlord_id):
        raise RoomNotFoundError()

    return crud_payment.get_lease_payments(db, lease_id=lease_id, skip=skip, limit=limit)


def fetch_tenant_lease_payments(
        db: Session,
        lease_id: int,
        tenant_id: int,
        skip: Optional[int],
        limit: Optional[int]
):
    lease = crud_lease.get(db, item_id=lease_id)

    if not lease:
        raise LeaseNotFoundError()

    if not verify_tenant_owns_lease(lease=lease, tenant_id=tenant_id):
        raise LeaseNotFoundError()

    return crud_payment.get_lease_payments(db, lease_id=lease_id, skip=skip, limit=limit)
