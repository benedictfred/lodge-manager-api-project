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

def test_landlord_create_lease_room_already_has_active_lease_returns_400(authenticated_landlord_client, mock_lease_schema,
                                                                         add_active_lease_to_db):
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


# --- Pagination Tests for Getting Leases (Landlord) ---

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


# --- Pagination Tests for Getting Leases (Tenant) ---

def test_tenant_get_personal_lease_history_returns_200(auth_client_factory, tenant_lease_history_in_db):
    """
    Tests that a tenant can get a paginated list of all their own leases.
    """
    tenant, db_leases = tenant_lease_history_in_db
    
    # We must construct a new authenticated client specifically for this newly created tenant
    # to avoid using the default authenticated_tenant_client which represents a different user.
    client = auth_client_factory(user_id=tenant.user_id)
    
    response = client.get(f'{lease_url}/tenant/me')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(db_leases)
    # Verify they all belong to the tenant
    for lease in data:
        assert lease['tenant_id'] == tenant.id

def test_tenant_get_personal_lease_history_pagination_limit(auth_client_factory, tenant_lease_history_in_db):
    """
    Verifies that the limit parameter restricts the number of returned personal leases.
    """
    tenant, db_leases = tenant_lease_history_in_db
    client = auth_client_factory(user_id=tenant.user_id)
    limit = 2
    
    response = client.get(f'{lease_url}/tenant/me?max_limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit

def test_tenant_get_personal_lease_history_pagination_skip(auth_client_factory, tenant_lease_history_in_db):
    """
    Verifies that the skip parameter correctly offsets the returned personal leases.
    """
    tenant, db_leases = tenant_lease_history_in_db
    client = auth_client_factory(user_id=tenant.user_id)
    skip = 1
    limit = 3
    
    response = client.get(f'{lease_url}/tenant/me?skip={skip}&max_limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit
    assert data[0]['id'] == db_leases[skip].id

def test_tenant_get_personal_lease_history_skip_exceeds_total(auth_client_factory, tenant_lease_history_in_db):
    """
    Verifies that skipping more personal leases than exist returns an empty list.
    """
    tenant, db_leases = tenant_lease_history_in_db
    client = auth_client_factory(user_id=tenant.user_id)
    total_leases = len(db_leases)
    
    response = client.get(f'{lease_url}/tenant/me?skip={total_leases + 5}&max_limit=5')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0

@pytest.mark.parametrize("status_filter", [
    LeaseStatus.ACTIVE,
    LeaseStatus.EXPIRED
])
def test_tenant_get_personal_lease_history_with_status_filter_returns_200(auth_client_factory, tenant_lease_history_in_db, status_filter):
    """
    Verifies that the status query parameter correctly filters the tenant's personal leases.
    """
    tenant, db_leases = tenant_lease_history_in_db
    client = auth_client_factory(user_id=tenant.user_id)
    
    response = client.get(f'{lease_url}/tenant/me?status={status_filter.value}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    # Filter the fixture leases manually to know the expected count
    expected_filtered_leases = [lease for lease in db_leases if lease.status == status_filter]

    assert len(data) == len(expected_filtered_leases)

    # Check that all returned leases have the correct status and belong to the tenant
    for lease in data:
        assert lease['status'] == status_filter.value
        assert lease['tenant_id'] == tenant.id

def test_landlord_cannot_get_tenant_lease_history_returns_403(authenticated_landlord_client):
    """
    Tests that a landlord cannot access the tenant's endpoint for getting personal lease history.
    """
    response = authenticated_landlord_client.get(f'{lease_url}/tenant/me')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only tenants are allowed.'


# --- Lease Termination Tests (Landlord) ---

def test_landlord_terminate_active_lease_returns_200(authenticated_landlord_client, add_active_lease_to_db):
    """
    Tests that a landlord can successfully terminate an ACTIVE lease.
    """
    lease_id = add_active_lease_to_db.id
    response = authenticated_landlord_client.patch(f'{lease_url}/terminate/{lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['status'] == LeaseStatus.TERMINATED.value
    # Assuming your model returns the updated end_date
    assert data['end_date'] is not None 

def test_landlord_terminate_non_existent_lease_returns_404(authenticated_landlord_client):
    """
    Tests that a landlord gets a 404 when trying to terminate a non-existent lease.
    """
    fake_lease_id = 9999
    response = authenticated_landlord_client.patch(f'{lease_url}/terminate/{fake_lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

@pytest.mark.parametrize("fixture_name", [
    "add_terminated_lease_to_db",
    "add_expired_lease_to_db"
])
def test_landlord_terminate_invalid_status_lease_returns_400(authenticated_landlord_client, request, fixture_name):
    """
    Tests that a landlord cannot terminate a lease that is already TERMINATED or EXPIRED.
    """
    lease = request.getfixturevalue(fixture_name)
    response = authenticated_landlord_client.patch(f'{lease_url}/terminate/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"Lease is already {lease.status.value}" in data['detail']

def test_landlord_terminate_lease_not_owned_returns_404(authenticated_landlord_client, add_active_lease_to_db,
                                                        add_active_lease_to_diff_landlord_lodge):
    """
    Tests that a landlord cannot terminate a lease belonging to a room in another landlord's lodge.
    """

    response = authenticated_landlord_client.patch(f'{lease_url}/terminate/{add_active_lease_to_diff_landlord_lodge.id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Room could not be found" in data['detail']


# --- Lease Termination Appeal Tests (Tenant) ---

def test_tenant_appeal_active_lease_returns_200(authenticated_tenant_client, add_active_lease_to_db):
    """
    Tests that a tenant can successfully appeal to terminate their own ACTIVE lease.
    """
    
    response = authenticated_tenant_client.patch(f'{lease_url}/me/terminate/{add_active_lease_to_db.id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['status'] == LeaseStatus.PENDING_TERMINATION.value

def test_tenant_appeal_non_existent_lease_returns_404(authenticated_tenant_client):
    """
    Tests that a tenant gets a 404 when trying to appeal a non-existent lease.
    """
    fake_lease_id = 9999
    response = authenticated_tenant_client.patch(f'{lease_url}/me/terminate/{fake_lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

def test_tenant_appeal_lease_not_owned_returns_404(authenticated_tenant_client, add_second_tenant_to_db):
    """
    Tests that a tenant cannot appeal a lease that belongs to another tenant.
    """
    # Authenticate as Tenant B
    diff_tenant_id = add_second_tenant_to_db.id

    response = authenticated_tenant_client.patch(f'{lease_url}/me/terminate/{diff_tenant_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

@pytest.mark.parametrize("fixture_name", [
    "add_terminated_lease_to_db",
    "add_expired_lease_to_db",
    "add_pending_termination_lease_to_db"
])
def test_tenant_appeal_invalid_status_lease_returns_400(authenticated_tenant_client, request, fixture_name):
    """
    Tests that a tenant cannot appeal a lease that is already TERMINATED, EXPIRED, or PENDING_TERMINATION.
    """
    lease = request.getfixturevalue(fixture_name)
    
    response = authenticated_tenant_client.patch(f'{lease_url}/me/terminate/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert  data['detail'] == f"Lease is already {lease.status.value}"

# --- Cross-Role Authorization Tests ---

def test_tenant_cannot_create_lease_returns_403(authenticated_tenant_client, mock_lease_schema):
    """
    Tests that a tenant cannot access the endpoint for creating a lease.
    """
    payload = mock_lease_schema.model_dump(mode='json')
    response = authenticated_tenant_client.post(lease_url, json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'

def test_tenant_cannot_terminate_lease_returns_403(authenticated_tenant_client, add_active_lease_to_db):
    """
    Tests that a tenant cannot access the landlord's endpoint for terminating a lease.
    """
    lease_id = add_active_lease_to_db.id
    response = authenticated_tenant_client.patch(f'{lease_url}/terminate/{lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'

def test_landlord_cannot_appeal_for_termination_returns_403(authenticated_landlord_client, add_active_lease_to_db):
    """
    Tests that a landlord cannot access the tenant's endpoint for appealing for termination.
    """
    lease_id = add_active_lease_to_db.id
    response = authenticated_landlord_client.patch(f'{lease_url}/me/terminate/{lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only tenants are allowed.'
