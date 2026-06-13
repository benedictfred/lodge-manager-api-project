from enum import Enum
from typing import Optional, Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict
from app.core.enums import BadgeTexts, BadgeVariants, RoomStatus
from app.schemas.entity_count import EntityCountResponse
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.schemas.room import RoomGridSummary


class LandlordDashboardStats(BaseModel):
    financials: FinancialResponse
    entity_counts: EntityCountResponse
    occupied_rooms_lease: OccupiedRoomLeasesResponse
    vacant_rooms: list[RoomGridSummary]
    maintenance_rooms: list[RoomGridSummary]

    model_config = ConfigDict(from_attributes=True)

class DashboardFilters(BaseModel):
    room_status_filters: list[RoomStatus]
    financial_filters: list[BadgeTexts]


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
            'owing': [],

        },
        'maintenance_rooms': [],
        'vacant_rooms': []
    }
    print(LandlordDashboardStats(**mock_dashboard_stats_dict).model_dump_json(indent=4))
