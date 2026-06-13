from typing import Optional

from app.crud.lodge import crud_lodge
from app.models.room import RoomFilter
from sqlalchemy.orm import Session
from app.core.enums import BadgeTexts
from app.crud.payment import crud_payment
from app.schemas.dashboard import LandlordDashboardStats, DashboardFilters
from app.schemas.entity_count import EntityCountResponse, OccupiedCounts
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.crud.room import crud_room
from app.schemas.room import RoomStatusCounts, RoomGridSummary
from app.services import lodge_service
from typing import Union
from app.core.enums import RoomStatus


def get_financial_summary(db: Session, lodge_id: int, filter_by: DashboardFilters):
    potential_revenue = crud_payment.get_potential_income_from_rooms(db, lodge_id=lodge_id)
    active_lease_financials = crud_payment.get_financials_for_active_leases(db, lodge_id=lodge_id, filter_by=filter_by)
    unpaid_rent = crud_payment.get_total_unpaid_rent(db, lodge_id=lodge_id, filter_by=filter_by)

    return FinancialResponse(
        potential_revenue=potential_revenue,
        expected_revenue= active_lease_financials.get('expected_revenue'),
        collected_revenue=active_lease_financials.get('collected_revenue'),
        unpaid_rent=unpaid_rent
    )


def get_room_dashboard_summary(
        db: Session,
        lodge_id: int,
        rooms: RoomFilter,
        filter_by: DashboardFilters,
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    # occupied rooms
    raw_rooms = crud_room.get_dashboard_rooms(db, filter_by=filter_by, lodge_id=lodge_id, skip=skip, limit=limit)
    categorized_rooms = [RoomGridSummary(**row) for row in raw_rooms]

    rooms.safe = [room for room in categorized_rooms if room.badge_text == BadgeTexts.SAFE]
    rooms.expiring = [room for room in categorized_rooms if room.badge_text == BadgeTexts.EXPIRING]
    rooms.overdue = [room for room in categorized_rooms if room.badge_text == BadgeTexts.OVERDUE]
    rooms.owing = [room for room in categorized_rooms if room.badge_text == BadgeTexts.OWING]

    # vacant rooms
    rooms.vacant = [room for room in categorized_rooms if room.badge_text == RoomStatus.VACANT]
    #maintenance rooms
    rooms.maintenance = [room for room in categorized_rooms if room.badge_text == RoomStatus.MAINTENANCE]

    return OccupiedRoomLeasesResponse(
        safe=rooms.safe,
        expiring=rooms.expiring,
        overdue=rooms.overdue,
        owing=rooms.owing
    )


def get_entity_count_summary(db: Session, lodge_id: int):
    room_status_counts =crud_lodge.get_room_status_counts(db, lodge_id=lodge_id)
    total_rooms = {'total_rooms': sum(room_status_counts.values()) if room_status_counts else 0}
    total_tenants = crud_lodge.get_tenant_counts(db, lodge_id=lodge_id)
    occupied_count = crud_lodge.get_occupied_counts(db, lodge_id=lodge_id)

    total_entity_counts = EntityCountResponse(
        **total_rooms,
        **total_tenants,
        room_status_counts=RoomStatusCounts(**room_status_counts),
        occupied_counts=OccupiedCounts(**occupied_count)
    )
    return total_entity_counts



def get_landlord_dashboard(
        db: Session,
        lodge_id: int,
        landlord_id: int,
        filter_by: DashboardFilters,
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    # check if the lodge exist and is owned by the landlord
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    #TODO: SUM ALL financial for the landlords revenue(expected, collected & outstanding)
    financials = get_financial_summary(db, lodge_id=lodge_id, filter_by=filter_by)
    print(financials.model_dump_json(indent=4))
    # Todo: count all the entities tied to the landlord's lodge( rooms, tenant, room statuses)
    entity_count = get_entity_count_summary(db, lodge_id=lodge_id)
    print(entity_count.model_dump_json(indent=4))
    #Todo: group rooms into occupied(safe, expiring & overdue) , vacant & maintenance
    rooms = RoomFilter()

    occupied_rooms_lease = get_room_dashboard_summary(
        db, lodge_id=lodge_id,
        rooms=rooms, filter_by=filter_by,
        skip=skip, limit=limit
    )

    dashboard_stats = LandlordDashboardStats(
        financials=financials,
        entity_counts=entity_count,
        occupied_rooms_lease=occupied_rooms_lease,
        maintenance_rooms=rooms.maintenance,
        vacant_rooms=rooms.vacant,
    )
    return dashboard_stats