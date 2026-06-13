from typing import Optional

from app.crud.lodge import crud_lodge
from app.models.room import RoomFilter
from sqlalchemy.orm import Session
from app.core.enums import BadgeTexts
from app.crud.payment import crud_payment
from app.schemas.dashboard import LandlordDashboardStats
from app.schemas.entity_count import EntityCountResponse
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.crud.room import crud_room
from app.services import lodge_service
from typing import Union
from app.core.enums import RoomStatus


def get_financial_summary(db: Session, lodge_id: int):
    potential_revenue = crud_payment.get_potential_income_from_rooms(db, lodge_id=lodge_id) or 0
    active_lease_financials = crud_payment.get_financials_for_active_leases(db, lodge_id=lodge_id)
    unpaid_rent = crud_payment.get_total_unpaid_rent(db, lodge_id=lodge_id) or 0

    return FinancialResponse(
        potential_revenue=potential_revenue,
        expected_revenue=dict(active_lease_financials).get('expected_revenue') or 0,
        collected_revenue=dict(active_lease_financials).get('collected_revenue') or 0,
        unpaid_rent=unpaid_rent
    )


def get_room_dashboard_summary(
        db: Session,
        lodge_id: int,
        rooms: RoomFilter,
        filter_by: Union[BadgeTexts, RoomStatus] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    # occupied rooms
    if not filter_by:
        rooms.safe = crud_room.get_dashboard_rooms(db, filter_by=BadgeTexts.SAFE, lodge_id=lodge_id, skip=skip,
                                                   limit=limit)
        rooms.expiring = crud_room.get_dashboard_rooms(db, filter_by=BadgeTexts.EXPIRING, lodge_id=lodge_id, skip=skip,
                                                       limit=limit)
        rooms.overdue = crud_room.get_dashboard_rooms(db, filter_by=BadgeTexts.OVERDUE, lodge_id=lodge_id, skip=skip,
                                                      limit=limit)
        rooms.owing = crud_room.get_dashboard_rooms(db, filter_by=BadgeTexts.OWING, lodge_id=lodge_id, skip=skip,
                                                    limit=limit)
        # vacant rooms
        rooms.vacant = crud_room.get_dashboard_rooms(db, filter_by=RoomStatus.VACANT, lodge_id=lodge_id, skip=skip,
                                                     limit=limit)
        #maintenance rooms
        rooms.maintenance = crud_room.get_dashboard_rooms(db, filter_by=RoomStatus.MAINTENANCE, lodge_id=lodge_id,
                                                          skip=skip, limit=limit)

    else:
        filtered_rooms = crud_room.get_dashboard_rooms(db, filter_by=filter_by, lodge_id=lodge_id, skip=skip,
                                                       limit=limit)
        filter_badge_text = filtered_rooms[0].badge_text.lower()
        setattr(rooms, filter_badge_text, filtered_rooms)

    return OccupiedRoomLeasesResponse(
        safe=rooms.safe,
        expiring=rooms.expiring,
        overdue=rooms.overdue,
        owing=rooms.owing
    )


def get_entity_count_summary(db: Session, lodge_id: int):
   total_entities =  crud_lodge.get_all_entities_count(db, lodge_id)
   entity_counts = EntityCountResponse(
       total_rooms= total_entities.

   )



def get_landlord_dashboard(
        db: Session,
        lodge_id: int,
        landlord_id: int,
        filter_by: Union[BadgeTexts, RoomStatus] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    # check if the lodge exist and is owned by the landlord
    lodge_service.verify_lodge_ownership(lodge_id=lodge_id, landlord_id=landlord_id)

    #TODO: SUM ALL financial for the landlords revenue(expected, collected & outstanding)
    financials = get_financial_summary(db, lodge_id=lodge_id)

    # Todo: count all the entities tied to the landlord's lodge( rooms, tenant, room statuses)
    #count rooms , tenants, vacant, maintenance, occupied, safe , expiring, owing, overdue
    #count because we want the totals across the entire property
    entity_count = get_entity_count_summary(db, lodge_id=lodge_id)
    #Todo: group rooms into occupied(safe, expiring & overdue) , vacant & maintenance
    rooms = RoomFilter()

    occupied_rooms_lease = get_room_dashboard_summary(
        db, lodge_id=lodge_id,
        rooms=rooms, filter_by=filter_by,
        skip=skip, limit=limit
    )

    dashboard_stats = LandlordDashboardStats(
        financials=financials,
        entity_counts= entity_count,
        occupied_rooms_lease=occupied_rooms_lease,
        maintenance_rooms=rooms.maintenance,
        vacant_rooms=rooms.vacant,
    )
