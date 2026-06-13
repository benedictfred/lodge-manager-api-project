
import pytest
from fastapi import status

from app.core.enums import RoomStatus
from test.conftest import base_url

dashboard_url = f'{base_url}/dashboard-landlord'

def test_landlord_get_paginated_dashboard_stats(authenticated_landlord_client, add_dashboard_stats):
    #authenticated landlord,
    #a fixture adds random payment amt to a list of leases , adds vacant rooms, maintenance rooms
    #it shd decide when to make complete payment,
    """"""
    lodge_id = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert 'financials' in data
    assert 'entity_counts' in data
    assert 'occupied_rooms_lease' in data
    assert 'maintenance_rooms' in data
    assert 'vacant_rooms' in data

def test_landlord_dashboard_pagination(authenticated_landlord_client, add_dashboard_stats):
    lodge_id = add_dashboard_stats

    # Test skip and limit (e.g., skip=0, limit=1 room in the grids)
    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}?skip=0&limit=1')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    
    # Limit applies to get_dashboard_rooms, so the total sum of categorized rooms + vacant + maintenance will be <= 1.
    total_rooms_in_arrays = (
        len(data['occupied_rooms_lease']['safe']) +
        len(data['occupied_rooms_lease']['expiring']) +
        len(data['occupied_rooms_lease']['overdue']) +
        len(data['occupied_rooms_lease']['owing']) +
        len(data['vacant_rooms']) +
        len(data['maintenance_rooms'])
    )
    assert total_rooms_in_arrays <= 1


def test_landlord_dashboard_filter_by_room_status(authenticated_landlord_client, add_dashboard_stats):
    lodge_id = add_dashboard_stats

    response = authenticated_landlord_client.get(
        url=f'{dashboard_url}/me/landlord/{lodge_id}',
        params={'room_statuses': [RoomStatus.VACANT.value]}
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['vacant_rooms']) > 0
    assert len(data['maintenance_rooms']) == 0
    assert len(data['occupied_rooms_lease']['safe']) == 0
    assert len(data['occupied_rooms_lease']['expiring']) == 0
    assert len(data['occupied_rooms_lease']['owing']) == 0


def test_landlord_dashboard_multiple_filters_combo(authenticated_landlord_client, add_dashboard_stats):
    lodge_id = add_dashboard_stats

    # Test multi-select: VACANT and OWING
    response = authenticated_landlord_client.get(
        url=f'{dashboard_url}/me/landlord/{lodge_id}',
        params={
            'room_statuses': [RoomStatus.VACANT.value],
            'financial_filters': ['Owing']
        }
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    # Should contain both vacant rooms and owing rooms, but NO safe or maintenance rooms
    assert len(data['vacant_rooms']) > 0
    assert len(data['occupied_rooms_lease']['owing']) > 0
    assert len(data['maintenance_rooms']) == 0
    assert len(data['occupied_rooms_lease']['safe']) == 0


def test_landlord_dashboard_unauthorized_snooper(authenticated_landlord_client, add_diff_landlord_lodge):
    # This lodge is owned by a DIFFERENT landlord
    lodge_id = add_diff_landlord_lodge.id

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_landlord_dashboard_empty_lodge(authenticated_landlord_client, add_lodge_to_db):
    lodge_id = add_lodge_to_db.id

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    # Empty lodge financials should all be 0 (Testing the func.coalesce safety)
    assert data['financials']['potential_revenue'] == 0
    assert data['financials']['expected_revenue'] == 0
    assert data['financials']['collected_revenue'] == 0
    assert data['financials']['unpaid_rent'] == 0

    # Empty entity counts
    assert data['entity_counts']['total_rooms'] == 0
    assert data['entity_counts']['total_tenants'] == 0

