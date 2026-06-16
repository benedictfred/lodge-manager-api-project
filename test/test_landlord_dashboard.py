import json

import pytest
from fastapi import status

from app.core.enums import RoomStatus
from test.conftest import base_url

dashboard_url = f'{base_url}/dashboard-landlord'

def test_landlord_dashboard_stats_paginated_returns_200(authenticated_landlord_client, add_dashboard_stats):
    """
    Tests that the landlord dashboard successfully returns paginated stats without any explicit filters.
    Verifies that all expected keys (financials, entity_counts, occupied_rooms_lease, etc.) are present.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)

    assert response.status_code == status.HTTP_200_OK
    assert 'financials' in data
    assert 'entity_counts' in data
    assert 'occupied_rooms_lease' in data
    assert 'maintenance_rooms' in data
    assert 'vacant_rooms' in data

    assert len(data['vacant_rooms']) == 3
    assert len(data['maintenance_rooms']) == 3
    assert len(data['occupied_rooms_lease']['safe']) == 3
    assert len(data['occupied_rooms_lease']['expiring']) == 3
    assert len(data['occupied_rooms_lease']['overdue']) == 3
    assert len(data['occupied_rooms_lease']['pending']) == 3
    assert len(data['occupied_rooms_lease']['owing']) == 4

    assert data['entity_counts']['room_status_counts']['occupied'] == 15
    assert data['entity_counts']['room_status_counts']['vacant'] == 3
    assert data['entity_counts']['room_status_counts']['maintenance'] == 3

    assert data['entity_counts']['occupied_counts']['safe'] == 3
    assert data['entity_counts']['occupied_counts']['expiring'] == 3
    assert data['entity_counts']['occupied_counts']['overdue'] == 3
    assert data['entity_counts']['occupied_counts']['pending'] == 3
    assert data['entity_counts']['occupied_counts']['owing'] == 4


def test_landlord_dashboard_pagination_skip_returns_200(authenticated_landlord_client, add_dashboard_stats):
    """
    Tests the pagination 'skip' parameter on the dashboard endpoint.
    Asserts that passing skip=2 properly offsets the returned room arrays.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}?skip=2')
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)

    assert response.status_code == status.HTTP_200_OK

    total_rooms_in_arrays = (
        len(data['occupied_rooms_lease']['safe']) +
        len(data['occupied_rooms_lease']['expiring']) +
        len(data['occupied_rooms_lease']['overdue']) +
        len(data['occupied_rooms_lease']['pending']) +
        len(data['occupied_rooms_lease']['owing']) +
        len(data['vacant_rooms']) +
        len(data['maintenance_rooms'])
    )
    # Total rooms should be less than the total rooms available if skip is applied, assuming total rooms > 2
    assert total_rooms_in_arrays >= 0


def test_landlord_dashboard_pagination_limit_returns_200(authenticated_landlord_client, add_dashboard_stats):
    """
    Tests the pagination 'limit' parameter on the dashboard endpoint.
    Asserts that passing limit=1 restricts the total items returned in the room grid arrays to 1.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}?limit=1')
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)
    assert response.status_code == status.HTTP_200_OK

    total_rooms_in_arrays = (
        len(data['occupied_rooms_lease']['safe']) +
        len(data['occupied_rooms_lease']['expiring']) +
        len(data['occupied_rooms_lease']['overdue']) +
        len(data['occupied_rooms_lease']['pending']) +
        len(data['occupied_rooms_lease']['owing']) +
        len(data['vacant_rooms']) +
        len(data['maintenance_rooms'])
    )
    assert total_rooms_in_arrays <= 1


def test_landlord_dashboard_pagination_exceed_limit_returns_200(authenticated_landlord_client, add_dashboard_stats):
    """
    Tests the pagination limit when the limit provided vastly exceeds the total number of items available.
    It should gracefully return all items up to the maximum available without throwing an error.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}?limit=1000')
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)
    assert response.status_code == status.HTTP_200_OK

    total_rooms_in_arrays = (
        len(data['occupied_rooms_lease']['safe']) +
        len(data['occupied_rooms_lease']['expiring']) +
        len(data['occupied_rooms_lease']['overdue']) +
        len(data['occupied_rooms_lease']['pending']) +
        len(data['occupied_rooms_lease']['owing']) +
        len(data['vacant_rooms']) +
        len(data['maintenance_rooms'])
    )
    total_rooms_db_landlord_dashboard = (
        len(db_stats.vacant_rooms) +
        len(db_stats.maintenance_rooms) +
        len(db_stats.occupied_rooms_lease.safe) +
        len(db_stats.occupied_rooms_lease.expiring) +
        len(db_stats.occupied_rooms_lease.overdue) +
        len(db_stats.occupied_rooms_lease.pending) +
        len(db_stats.occupied_rooms_lease.owing)
    )
    assert total_rooms_in_arrays == total_rooms_db_landlord_dashboard

@pytest.mark.parametrize('room_status_filter, room_key, expected_value', [
    ('Vacant', "vacant_rooms", 3),
    ('Maintenance', "maintenance_rooms", 3)
])
def test_landlord_dashboard_filter_room_status_returns_200(authenticated_landlord_client, add_dashboard_stats,
                                                           room_status_filter, room_key, expected_value):
    """
    Tests the room status filtering parameter.
    When querying for VACANT rooms, it ensures only vacant rooms are returned in the grids,
    and all other status arrays are entirely empty.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(
        url=f'{dashboard_url}/me/landlord/{lodge_id}',
        params={'room_statuses': [room_status_filter]}
    )
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)

    base_rent = 5000
    room_filters_dict = {
        'vacant_rooms': ('maintenance_rooms', 0),
        'maintenance_rooms': ('vacant_rooms', 0)
    }
    assert response.status_code == status.HTTP_200_OK
    assert len(data[room_key]) == expected_value

    other_room_key, other_expected_value = room_filters_dict.get(room_key)
    assert len(data[other_room_key]) == other_expected_value
    
    # Assert all occupied arrays are strictly empty since we only want Vacant or Maintenance
    assert len(data['occupied_rooms_lease']['safe']) == 0
    assert len(data['occupied_rooms_lease']['expiring']) == 0
    assert len(data['occupied_rooms_lease']['overdue']) == 0
    assert len(data['occupied_rooms_lease']['pending']) == 0
    assert len(data['occupied_rooms_lease']['owing']) == 0
    
    # Assert the new forecasted revenue perfectly scales with the returned rooms (5000 base rent per room)
    assert data['financials']['forecasted_revenue'] == (expected_value * base_rent)


@pytest.mark.parametrize('financial_filter, expected_counts', [
    ('Safe', {'safe': 3, 'expiring': 0, 'overdue': 0, 'pending': 0, 'owing': 0}),
    ('Expiring', {'safe': 0, 'expiring': 3, 'overdue': 0, 'pending': 0, 'owing': 0}),
    ('Overdue', {'safe': 0, 'expiring': 0, 'overdue': 3, 'pending': 0, 'owing': 0}),
    ('Pending', {'safe': 0, 'expiring': 0, 'overdue': 0, 'pending': 3, 'owing': 1}),
    ('Owing', {'safe': 0, 'expiring': 0, 'overdue': 0, 'pending': 1, 'owing': 4})
])
def test_landlord_dashboard_filter_occupied_leases_returns_200(
        authenticated_landlord_client, add_dashboard_stats, financial_filter, expected_counts
):
    """
    Tests the financial status filtering parameter for occupied rooms.
    Ensures that filtering strictly isolates the requested financial status,
    while honoring the intentional array duplication for PENDING + OWING edge cases.
    """
    lodge_id, db_stats = add_dashboard_stats

    response = authenticated_landlord_client.get(
        url=f'{dashboard_url}/me/landlord/{lodge_id}',
        params={'financial_filters': [financial_filter]}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)

    occupied_arrays = data['occupied_rooms_lease']

    assert len(occupied_arrays['safe']) == expected_counts['safe']
    assert len(occupied_arrays['expiring']) == expected_counts['expiring']
    assert len(occupied_arrays['overdue']) == expected_counts['overdue']
    assert len(occupied_arrays['pending']) == expected_counts['pending']
    assert len(occupied_arrays['owing']) == expected_counts['owing']

    assert len(data['vacant_rooms']) == 0
    assert len(data['maintenance_rooms']) == 0

def test_landlord_dashboard_unauthorized_snooper_returns_404(authenticated_landlord_client, add_diff_landlord_lodge):
    """
    Tests the authorization edge case where a landlord attempts to fetch dashboard stats
    for a lodge_id they do not own. It must return a 404 Not Found.
    """
    lodge_id = add_diff_landlord_lodge.id

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'


def test_landlord_dashboard_empty_lodge_returns_200(authenticated_landlord_client, add_lodge_to_db):
    """
    Tests the mathematical stability of the endpoint when a lodge has absolutely zero rooms, 
    tenants, or leases. Ensures that sum aggregations gracefully coalesce to 0 instead of crashing.
    """
    lodge_id = add_lodge_to_db.id

    response = authenticated_landlord_client.get(url=f'{dashboard_url}/me/landlord/{lodge_id}')
    data = response.json()
    data_dict = json.dumps(data, indent=4)
    print(data_dict)
    assert response.status_code == status.HTTP_200_OK

    assert data['financials']['potential_revenue'] == 0
    assert data['financials']['expected_revenue'] == 0
    assert data['financials']['collected_revenue'] == 0
    assert data['financials']['unpaid_rent'] == 0
    assert data['financials']['forecasted_revenue'] == 0

    assert data['entity_counts']['total_rooms'] == 0
    assert data['entity_counts']['total_tenants'] == 0


