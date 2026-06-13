from sqlalchemy import func, cast, Integer

from app.core.enums import RoomStatus, BadgeTexts
from app.crud.payment import crud_payment
from app.models.lease import Lease
from app.models.room import Room

days_left = cast(func.julianday(Lease.end_date) - func.julianday('now'), Integer)  # only supported by sqlite,
# change in production to postgres
payment_subq = crud_payment.get_payment_subq()
total_paid = func.coalesce(payment_subq.c.total_amt_paid, 0)

has_payed_in_full = total_paid == Lease.agreed_rent_amt
incomplete_payment = total_paid < Lease.agreed_rent_amt

occupied_expr = Room.status == RoomStatus.OCCUPIED
vacant_expr = Room.status == RoomStatus.VACANT
maintenance_expr = Room.status == RoomStatus.MAINTENANCE

filter_menu = {
    RoomStatus.OCCUPIED: occupied_expr,
    RoomStatus.VACANT: vacant_expr,
    RoomStatus.MAINTENANCE: maintenance_expr,
    BadgeTexts.SAFE: (occupied_expr, has_payed_in_full, days_left >= 90),
    BadgeTexts.EXPIRING: (occupied_expr, has_payed_in_full, days_left.between(0, 89)),
    BadgeTexts.OVERDUE: (occupied_expr, has_payed_in_full, days_left < 0),
    BadgeTexts.OWING: (occupied_expr, has_payed_in_full, incomplete_payment)
}