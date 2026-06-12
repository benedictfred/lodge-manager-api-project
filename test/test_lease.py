import pytest
from fastapi import status
from datetime import timedelta

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
    
    payload_second_lease = mock_lease_schema.model_dump(mode='json')
    response_second = authenticated_landlord_client.post(lease_url, json=payload_second_lease)
    data_second = response_second.json()

    assert response_second.status_code == status.HTTP_400_BAD_REQUEST
    assert "Lease is already Active" in data_second['detail']