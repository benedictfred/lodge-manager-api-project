"""
Pydantic schemas for the dashboard domain.

This module contains schemas used to structure the data for the landlord's dashboard,
including financial summaries, entity counts, and room statuses.
"""
from datetime import date
from enum import Enum
from typing import Optional, Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict
from app.core.enums import BadgeTexts, BadgeVariants, RoomStatus
from app.schemas.entity_count import EntityCountResponse
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse, LeaseBase
from app.schemas.room import RoomGridSummary, RoomCreate, RoomBase


class LandlordDashboardStats(BaseModel):
    """
    Schema representing the complete dashboard statistics for a landlord.

    Attributes:
        financials (FinancialResponse): The financial summary.
        entity_counts (EntityCountResponse): The counts of different entities.
        occupied_rooms_lease (OccupiedRoomLeasesResponse): The lease details of occupied rooms.
        vacant_rooms (list[RoomGridSummary]): The list of vacant rooms.
        maintenance_rooms (list[RoomGridSummary]): The list of rooms under maintenance.
    """
    financials: FinancialResponse
    entity_counts: EntityCountResponse
    occupied_rooms_lease: OccupiedRoomLeasesResponse
    vacant_rooms: list[RoomGridSummary]
    maintenance_rooms: list[RoomGridSummary]

    model_config = ConfigDict(from_attributes=True)

class DashboardFilters(BaseModel):
    """
    Schema for filtering dashboard statistics.

    Attributes:
        room_status_filters (list[RoomStatus]): Filters for room statuses.
        financial_filters (list[BadgeTexts]): Filters for financial categories.
    """
    room_status_filters: list[RoomStatus]
    financial_filters: list[BadgeTexts]

class RoomSummary(BaseModel):
    description: str
    base_rent: int
    status: str

class LeaseSummary(BaseModel):
    start_date: date
    end_date: date

class FinancialSummary(BaseModel):
    agreed_rent: int
    total_paid: int
    remaining_balance: int

class TenantSummary(BaseModel):
    name: str
    phone: str

class RoomLeaseInfo(BaseModel):
    room: RoomSummary
    lease: LeaseSummary
    finance: FinancialSummary
    tenant: TenantSummary

    pass
if __name__ == "__main__":
    mock_dashboard_stats_dict = {
        'financials': {
            'potential_revenue': 5000000,
            'expected_revenue': 4500000,
            'collected_revenue': 3500000,
            'unpaid_rent': 750000

        },
        'entity_counts': {
            'total_rooms': 40,
            'total_tenants': 35,
            'room_status_counts': {
                'occupied': 30,
                'vacant': 6,
                'maintenance': 4
            },
            'occupied_counts': {
                'safe': 10,
                'expiring': 10,
                'overdue': 2,
                'pending': 0,
                'owing': 8
            }
        },
        'occupied_rooms_lease': {
            'safe': [
                {
                    'lease_id': 1,
                    'room_no': '29',
                    'badge_text': BadgeTexts.SAFE,
                    'badge_variant': BadgeVariants.SUCCESS,
                    'main_display_text': 'Donald',
                    'sub_display_text': '91 days left'
                },
                {
                    'lease_id': 2,
                    'room_no': '30',
                    'badge_text': BadgeTexts.SAFE,
                    'badge_variant': BadgeVariants.SUCCESS,
                    'main_display_text': 'Philip',
                    'sub_display_text': '120 days left'
                },
                {
                    'lease_id': 3,
                    'room_no': '31',
                    'badge_text': BadgeTexts.SAFE,
                    'badge_variant': BadgeVariants.SUCCESS,
                    'main_display_text': 'James',
                    'sub_display_text': '101 days left'
                },

            ],
            'expiring': [
                {
                    'lease_id': 1,
                    'room_no': '29',
                    'badge_text': BadgeTexts.EXPIRING,
                    'badge_variant': BadgeVariants.WARNING,
                    'main_display_text': 'Donald',
                    'sub_display_text': '91 days left'
                },
                {
                    'lease_id': 2,
                    'room_no': '30',
                    'badge_text': BadgeTexts.EXPIRING,
                    'badge_variant': BadgeVariants.WARNING,
                    'main_display_text': 'Philip',
                    'sub_display_text': '120 days left'
                },
                {
                    'lease_id': 3,
                    'room_no': '31',
                    'badge_text': BadgeTexts.EXPIRING,
                    'badge_variant': BadgeVariants.WARNING,
                    'main_display_text': 'James',
                    'sub_display_text': '101 days left'
                },
            ],
            'overdue': [
                {
                    'lease_id': 1,
                    'room_no': '29',
                    'badge_text': BadgeTexts.OVERDUE,
                    'badge_variant': BadgeVariants.DANGER,
                    'main_display_text': 'Donald',
                    'sub_display_text': '91 days left'
                },
                {
                    'lease_id': 2,
                    'room_no': '30',
                    'badge_text': BadgeTexts.OVERDUE,
                    'badge_variant': BadgeVariants.DANGER,
                    'main_display_text': 'Philip',
                    'sub_display_text': '120 days left'
                },
                {
                    'lease_id': 3,
                    'room_no': '31',
                    'badge_text': BadgeTexts.OVERDUE,
                    'badge_variant': BadgeVariants.INFO,
                    'main_display_text': 'danger',
                    'sub_display_text': '101 days left'
                },
            ],
            'pending': [],
            'owing': [],

        },
        'maintenance_rooms': [],
        'vacant_rooms': []
    }
    print(LandlordDashboardStats(**mock_dashboard_stats_dict).model_dump_json(indent=4))
