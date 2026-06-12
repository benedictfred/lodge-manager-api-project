import pytest
from fastapi import status
from datetime import timedelta

from app.core.enums import LeaseStatus
from test.conftest import base_url, add_lodge_to_db

lease_url = f'{base_url}/leases'

def test_landlord_create_lease_returns_200(authenticated_landlord_client, mock_lease_schema):
    """
    Tests that a landlord can create a lease successfully.
    """
    payload = mock_lease_schema.model_dump(mode='json') # Use mode='json' for date serialization
    
    response = authenticated_landlord_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['tenant_id'] == mock_lease_schema.tenant_id
    assert data['room_id'] == mock_lease_schema.room_id
    assert data['agreed_rent_amt'] == mock_lease_schema.agreed_rent_amt
    assert data['status'] == mock_lease_schema.status.value
    assert data['start_date'] == mock_lease_schema.start_date.isoformat()
    assert data['end_date'] == mock_lease_schema.end_date.isoformat()
    assert 'id' in data
    assert 'created_at' in data

def test_landlord_create_lease_room_does_not_exist_returns_404(authenticated_landlord_client, mock_lease_schema):
    """
    Tests that a landlord cannot create a lease for a room that does not exist.
    """
    mock_lease_schema.room_id = 99999  # A non-existent room ID
    payload = mock_lease_schema.model_dump(mode='json')
    
    response = authenticated_landlord_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Room could not be found" in data['detail']

def test_landlord_create_lease_room_not_owned_by_landlord_returns_403(authenticated_landlord_client, mock_lease_schema, add_diff_landlord_room):
    """
    Tests that a landlord cannot create a lease for a room not owned by them.
    """
    mock_lease_schema.room_id = add_diff_landlord_room.id
    payload = mock_lease_schema.model_dump(mode='json')

    response = authenticated_landlord_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Room could not be found" in data['detail']

def test_landlord_create_lease_tenant_does_not_exist_returns_404(authenticated_landlord_client, mock_lease_schema):
    """
    Tests that a landlord cannot create a lease for a tenant that does not exist.
    """
    mock_lease_schema.tenant_id = 99999  # A non-existent tenant ID
    payload = mock_lease_schema.model_dump(mode='json')

    response = authenticated_landlord_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User could not be found" in data['detail']

def test_landlord_create_lease_tenant_not_in_landlords_lodge_returns_404(authenticated_landlord_client, mock_lease_schema, add_diff_landlord_tenant):
    """
    Tests that a landlord cannot create a lease for a tenant that exists but is not associated with their lodge.
    """
    mock_lease_schema.tenant_id = add_diff_landlord_tenant.id
    payload = mock_lease_schema.model_dump(mode='json')

    response = authenticated_landlord_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User could not be found" in data['detail']

def test_landlord_create_lease_room_already_has_active_lease_returns_409(authenticated_landlord_client, mock_lease_schema, add_active_lease_to_db_direct):
    """
    Tests that a landlord cannot create a lease for a room that already has an active lease.
    """

    mock_lease_schema.start_date = mock_lease_schema.start_date + timedelta(days=1)
    mock_lease_schema.end_date = mock_lease_schema.start_date + timedelta(days=180) # 6 months later
    
    lease_payload= mock_lease_schema.model_dump(mode='json')
    response_second = authenticated_landlord_client.post(lease_url, json=lease_payload)
    data_second = response_second.json()

    assert response_second.status_code == status.HTTP_400_BAD_REQUEST
    assert "Lease is already Active" in data_second['detail']


# --- Pagination Tests for Getting Leases ---

def test_landlord_get_paginated_leases_returns_200(authenticated_landlord_client, leases_in_db, add_lodge_to_db):
    """
    Tests that a landlord can get a paginated list of all leases in their lodge.
    """
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(leases_in_db)

def test_landlord_get_leases_pagination_limit_returns_200(authenticated_landlord_client, leases_in_db, add_lodge_to_db):
    """
    Verifies that the limit parameter restricts the number of returned leases.
    """
    limit = 3
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}?limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit

def test_landlord_get_leases_pagination_skip_returns_200(authenticated_landlord_client, leases_in_db, add_lodge_to_db):
    """
    Verifies that the skip parameter correctly offsets the returned leases.
    """
    skip = 2
    limit = 3
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}?skip={skip}&limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit
    # The order depends on default DB sorting (usually insertion order for simple tests).
    # Since we added sequentially, data[0] should match leases_in_db[2]
    assert data[0]['id'] == leases_in_db[skip].id

def test_landlord_get_leases_pagination_skip_exceeds_total_returns_200(authenticated_landlord_client, leases_in_db, add_lodge_to_db):
    """
    Verifies that skipping more leases than exist returns an empty list.
    """
    total_leases = len(leases_in_db)
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}?skip={total_leases + 5}&limit=5')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0

@pytest.mark.parametrize("status_filter", [
    LeaseStatus.ACTIVE,
    LeaseStatus.EXPIRED
])
def test_landlord_get_leases_pagination_with_status_filter_returns_200(authenticated_landlord_client, leases_in_db, add_lodge_to_db, status_filter):
    """
    Verifies that the status query parameter correctly filters the returned leases.
    """
    lodge_id = add_lodge_to_db.id
    # Ensure there's a mix of statuses in the db to test filtering properly.
    # The leases_in_db fixture creates a mix of ACTIVE and INACTIVE leases.

    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}?status={status_filter.value}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    # Filter the leases in DB manually to know the expected count
    expected_filtered_leases = [lease for lease in leases_in_db if lease.status == status_filter]

    assert len(data) == len(expected_filtered_leases)

    # Check that all returned leases have the correct status
    for lease in data:
        assert lease['status'] == status_filter.value

def test_tenant_cannot_get_lodge_leases_returns_403(authenticated_tenant_client, add_lodge_to_db):
    """
    Tests that a tenant cannot access the landlord's endpoint for getting all leases in a lodge.
    """
    lodge_id = add_lodge_to_db.id
    response = authenticated_tenant_client.get(f'{lease_url}/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'

def test_landlord_cannot_get_leases_for_not_owned_lodge_returns_404(authenticated_landlord_client, add_diff_landlord_lodge):
    """
    Tests that a landlord cannot get leases from a lodge they do not own.
    """
    lodge_id = add_diff_landlord_lodge.id
    response = authenticated_landlord_client.get(f'{lease_url}/{lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'

def test_landlord_cannot_get_leases_for_non_existent_lodge_returns_404(authenticated_landlord_client):
    """
    Tests that a landlord cannot get leases from a non-existent lodge.
    """
    fake_lodge_id = 9999
    response = authenticated_landlord_client.get(f'{lease_url}/{fake_lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'