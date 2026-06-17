"""
Module providing dashboard-related business logic.

This module contains services for generating dashboard summaries.
"""
from datetime import date
from typing import Optional

from app.core.exceptions import LeaseNotFoundError
from app.crud.lease import crud_lease
from app.crud.lodge import crud_lodge
from app.models.lease import Lease
from app.models.room import RoomFilter
from sqlalchemy.orm import Session, joinedload
from app.core.enums import BadgeTexts
from app.crud.payment import crud_payment
from app.models.tenantprofile import TenantProfile
from app.schemas.dashboard import LandlordDashboardStats, DashboardFilters, RoomSummary, LeaseSummary, FinancialSummary, \
    TenantSummary, RoomLeaseInfo
from app.schemas.entity_count import EntityCountResponse, OccupiedCounts
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.crud.room import crud_room
from app.schemas.room import RoomStatusCounts, RoomGridSummary
from app.services import lodge_service
from typing import Union
from app.core.enums import RoomStatus


def get_financial_summary(db: Session, lodge_id: int, filter_by: DashboardFilters):
    """
    Get financial summary for a specific lodge.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        filter_by (DashboardFilters): Dashboard filters to apply.

    Returns:
        FinancialResponse: The financial summary details.
    """
    potential_revenue = crud_payment.get_potential_income_from_rooms(db, lodge_id=lodge_id)
    active_lease_financials = crud_payment.get_financials_for_active_leases(db, lodge_id=lodge_id, filter_by=filter_by)
    forecasted_revenue = crud_payment.get_financial_for_forecasted_empty_rooms(db, lodge_id=lodge_id, filter_by=filter_by)
    unpaid_rent = crud_payment.get_total_unpaid_rent(db, lodge_id=lodge_id, filter_by=filter_by)

    return FinancialResponse(
        potential_revenue=potential_revenue,
        expected_revenue= active_lease_financials.get('expected_revenue'),
        collected_revenue=active_lease_financials.get('collected_revenue'),
        forecasted_revenue=forecasted_revenue,
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
    """
    Get a dashboard summary of rooms in a specific lodge.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        rooms (RoomFilter): Filter object to hold categorized rooms.
        filter_by (DashboardFilters): Dashboard filters to apply.
        skip (Optional[int]): Number of records to skip. Defaults to None.
        limit (Optional[int]): Maximum number of records to return. Defaults to None.

    Returns:
        OccupiedRoomLeasesResponse: Summary of occupied room leases.
    """
    # occupied rooms
    raw_rooms = crud_room.get_dashboard_rooms(db, filter_by=filter_by, lodge_id=lodge_id, skip=skip, limit=limit)
    room_grids = [RoomGridSummary(**row) for row in raw_rooms]

    rooms.safe = [room for room in room_grids if room.badge_text == BadgeTexts.SAFE]
    rooms.expiring = [room for room in room_grids if room.badge_text == BadgeTexts.EXPIRING]
    rooms.overdue = [room for room in room_grids if room.badge_text == BadgeTexts.OVERDUE]
    rooms.pending = [room for room in room_grids if room.badge_text == BadgeTexts.PENDING]
    rooms.owing = [room for room in room_grids if room.badge_text == BadgeTexts.OWING or
                   (room.badge_text == BadgeTexts.PENDING and room.is_owing)]

    # vacant rooms
    rooms.vacant = [room for room in room_grids if room.badge_text == RoomStatus.VACANT]
    #maintenance rooms
    rooms.maintenance = [room for room in room_grids if room.badge_text == RoomStatus.MAINTENANCE]

    return OccupiedRoomLeasesResponse(
        safe=rooms.safe,
        expiring=rooms.expiring,
        overdue=rooms.overdue,
        pending=rooms.pending,
        owing=rooms.owing
    )


def get_entity_count_summary(db: Session, lodge_id: int):
    """
    Get the entity count summary for a specific lodge.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.

    Returns:
        EntityCountResponse: The entity count details.
    """
    room_status_counts =crud_lodge.get_room_status_counts(db, lodge_id=lodge_id)
    total_rooms_count = sum(room_status_counts.values()) if room_status_counts else 0
    total_rooms = {'total_rooms': total_rooms_count}
    total_tenants = crud_lodge.get_tenant_counts(db, lodge_id=lodge_id)
    occupied_count = crud_lodge.get_occupied_counts(db, lodge_id=lodge_id)
    
    occupied_rooms = room_status_counts.get('occupied', 0) if room_status_counts else 0
    occupancy_rate = int((occupied_rooms / total_rooms_count) * 100) if total_rooms_count > 0 else 0

    total_entity_counts = EntityCountResponse(
        **total_rooms,
        **total_tenants,
        room_status_counts=RoomStatusCounts(**room_status_counts) if room_status_counts else RoomStatusCounts(Occupied=0, Vacant=0, Maintenance=0),
        occupied_counts=OccupiedCounts(**occupied_count) if occupied_count else OccupiedCounts(safe=0, expiring=0, overdue=0, pending=0, owing=0),
        occupancy_rate=occupancy_rate
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
    """
    Get the dashboard statistics for a landlord.

    Args:
        db (Session): The database session.
        lodge_id (int): The ID of the lodge.
        landlord_id (int): The ID of the landlord.
        filter_by (DashboardFilters): Dashboard filters to apply.
        skip (Optional[int]): Number of records to skip. Defaults to None.
        limit (Optional[int]): Maximum number of records to return. Defaults to None.

    Returns:
        LandlordDashboardStats: The complete dashboard statistics.
    """
    # check if the lodge exist and is owned by the landlord
    lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_id)

    #TODO: SUM ALL financial for the landlords revenue(expected, collected & outstanding)
    financials = get_financial_summary(db, lodge_id=lodge_id, filter_by=filter_by)

    # Todo: count all the entities tied to the landlord's lodge( rooms, tenant, room statuses)
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
        entity_counts=entity_count,
        occupied_rooms_lease=occupied_rooms_lease,
        maintenance_rooms=rooms.maintenance,
        vacant_rooms=rooms.vacant,
    )
    return dashboard_stats

def _organise_room_lease_summary(
        db: Session,
        landlord_id: int,
        lease_id: int
):
    raw_summary_row = crud_lodge.get_room_lease_info(
        db,
        landlord_id=landlord_id,
        lease_id=lease_id
    )
    if not raw_summary_row:
        raise LeaseNotFoundError()

    room_summary = RoomSummary(**raw_summary_row)
    lease_summary = LeaseSummary(**raw_summary_row)
    financial_summary = FinancialSummary(**raw_summary_row)
    tenant_summary = TenantSummary(**raw_summary_row)
    
    return RoomLeaseInfo(
        room=room_summary,
        lease=lease_summary,
        tenant=tenant_summary,
        finance=financial_summary
    )

def get_dashboard_lease_info(
        db: Session,
        lease_id: int,
        landlord_id: int
):
    #lease exists and owned by landlord
    #crud to build a query that joins the room, lease, tenant, user, payment_subq together and bundle the necessary
    #info into in the select
    #then calculates balance in python b4  putting in the RoomLeaseInfo schema


    return _organise_room_lease_summary(
        db,
        landlord_id=landlord_id,
        lease_id=lease_id
    )

