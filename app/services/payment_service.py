"""
Module providing payment-related business logic.

This module contains services for managing payments.
"""
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
    """
    Check if a payment can be added based on the total payments and agreed amount.

    Args:
        total_payments (int): The total amount paid so far.
        incoming_amt (int): The incoming payment amount.
        agreed_amt (int): The total agreed amount for the lease.

    Returns:
        bool: True if the payment can be added, False otherwise.
    """
    return total_payments + incoming_amt <= agreed_amt


def add_payment_record(
        db: Session,
        current_landlord_id: int,
        payment_data: PaymentCreate
):
    """
    Add a new payment record.

    Args:
        db (Session): The database session.
        current_landlord_id (int): The ID of the current landlord.
        payment_data (PaymentCreate): The data for the new payment.

    Returns:
        Payment: The newly created payment record.
    """
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

    total_payments = crud_payment.get_payments_aggregate_by_lease_id(db, lease_id=lease.id)

    if not can_add_payment(total_payments=total_payments, incoming_amt=payment_data.amount_paid,
                           agreed_amt=lease.agreed_rent_amt):

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
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    """
    Fetch payments for a specific lease.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease.
        landlord_id (int): The ID of the landlord.
        skip (Optional[int]): Number of records to skip. Defaults to None.
        limit (Optional[int]): Maximum number of records to return. Defaults to None.

    Returns:
        list[Payment]: A list of payments for the lease.
    """
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
    """
    Fetch payments for a specific lease by a tenant.

    Args:
        db (Session): The database session.
        lease_id (int): The ID of the lease.
        tenant_id (int): The ID of the tenant.
        skip (Optional[int]): Number of records to skip.
        limit (Optional[int]): Maximum number of records to return.

    Returns:
        list[Payment]: A list of payments for the lease.
    """
    lease = crud_lease.get(db, item_id=lease_id)

    if not lease:
        raise LeaseNotFoundError()

    if not verify_tenant_owns_lease(lease=lease, tenant_id=tenant_id):
        raise LeaseNotFoundError()

    return crud_payment.get_lease_payments(db, lease_id=lease_id, skip=skip, limit=limit)
