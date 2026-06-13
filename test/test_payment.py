import pytest
from fastapi import status
from datetime import timedelta
from app.core.enums import LeaseStatus
from test.conftest import base_url

payment_url = f'{base_url}/payments'

# --- Create Payment Tests (Landlord) ---

def test_landlord_create_payment_returns_200(authenticated_landlord_client,add_active_lease_to_db, mock_payment_schema):
    """
    Tests that a landlord can successfully create a payment for an active lease.
    """
    mock_payment_schema.lease_id = add_active_lease_to_db.id
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['amount_paid'] == mock_payment_schema.amount_paid
    assert data['lease_id'] == mock_payment_schema.lease_id
    assert 'id' in data
    assert 'payment_date' in data

def test_landlord_create_payment_lease_does_not_exist_returns_404(authenticated_landlord_client, mock_payment_schema):
    """
    Tests that a landlord gets a 404 when trying to pay for a non-existent lease.
    """
    mock_payment_schema.lease_id = 99999
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

def test_landlord_create_payment_lease_not_owned_returns_404(authenticated_landlord_client, mock_payment_schema, add_active_lease_to_diff_landlord_lodge):
    """
    Tests that a landlord cannot pay for a lease in a lodge they don't own.
    """
    mock_payment_schema.lease_id = add_active_lease_to_diff_landlord_lodge.id
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Room could not be found'

@pytest.mark.parametrize("fixture_name", [
    "add_expired_lease_to_db",
    "add_terminated_lease_to_db",
    "add_pending_termination_lease_to_db"
])
def test_landlord_create_payment_inactive_lease_returns_400(authenticated_landlord_client, request, fixture_name):
    """
    Tests that a landlord cannot create a payment for an inactive lease.
    """
    lease = request.getfixturevalue(fixture_name)
    payload = {
        "amount_paid": 5000,
        "lease_id": lease.id
    }
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"Lease is already {lease.status.value}" in data['detail']

def test_landlord_create_payment_exceeds_agreed_rent_returns_400(authenticated_landlord_client, mock_payment_schema, add_active_lease_to_db):
    """
    Tests that adding a payment that pushes total above agreed amount fails.
    """
    # Assuming the fixture lease has some base rent price e.g., 210000
    mock_payment_schema.amount_paid = add_active_lease_to_db.agreed_rent_amt + 1000
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Remaining balance is" in data['detail']

def test_landlord_create_payment_negative_amount_returns_422(authenticated_landlord_client, mock_payment_schema):
    """
    Tests Pydantic validation catches negative payment amounts.
    """
    mock_payment_schema.amount_paid = -5000
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_landlord_client.post(f'{payment_url}/create-payment', json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_tenant_cannot_create_payment_returns_403(authenticated_tenant_client, mock_payment_schema):
    """
    Tests that a tenant cannot access the create payment endpoint.
    """
    payload = mock_payment_schema.model_dump(mode='json')
    response = authenticated_tenant_client.post(f'{payment_url}/create-payment', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'


# --- List Lease Payments Tests (Landlord) ---

def test_landlord_get_lease_payments_returns_200(authenticated_landlord_client, multiple_safe_payments_in_db):
    """
    Tests that a landlord can get the payment history of their lease.
    """
    db_payments, lease = multiple_safe_payments_in_db

    # There is 1 payment from lease creation + 5 from fixture = 6 payments
    response = authenticated_landlord_client.get(f'{payment_url}/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(db_payments)

def test_landlord_get_lease_payments_pagination_limit(authenticated_landlord_client, multiple_safe_payments_in_db):
    """
    Verifies that the limit parameter restricts returned payments.
    """
    db_payments, lease = multiple_safe_payments_in_db
    limit = 3
    response = authenticated_landlord_client.get(f'{payment_url}/{lease.id}?limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit

def test_landlord_get_lease_payments_pagination_skip(authenticated_landlord_client, multiple_safe_payments_in_db):
    """
    Verifies that the skip parameter correctly offsets the returned payments.
    """
    db_payments, lease = multiple_safe_payments_in_db
    skip = 2
    limit = 2
    response = authenticated_landlord_client.get(f'{payment_url}/{lease.id}?skip={skip}&limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit

    assert data[0]['id'] == db_payments[skip].id

def test_landlord_get_payments_lease_does_not_exist_returns_404(authenticated_landlord_client):
    """
    Tests getting payments for non-existent lease returns 404.
    """
    fake_lease_id = 9999
    response = authenticated_landlord_client.get(f'{payment_url}/{fake_lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

def test_landlord_get_payments_not_owned_lodge_returns_404(authenticated_landlord_client, add_active_lease_to_diff_landlord_lodge):
    """
    Tests getting payments for a lease not owned by the landlord.
    """
    lease_id = add_active_lease_to_diff_landlord_lodge.id
    response = authenticated_landlord_client.get(f'{payment_url}/{lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Room could not be found'


# --- List Tenant Payments Tests (Tenant) ---

def test_tenant_get_own_lease_payments_returns_200(auth_client_factory, tenant_safe_payments_in_db):
    """
    Tests that a tenant can retrieve their own lease payments.
    """
    db_payments, lease = tenant_safe_payments_in_db
    client = auth_client_factory(user_id=lease.tenant.user_id)

    response = client.get(f'{payment_url}/me/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(db_payments)

def test_tenant_get_own_lease_payments_pagination_limit(auth_client_factory, tenant_safe_payments_in_db):
    """
    Verifies that the limit parameter restricts returned personal payments.
    """
    db_payments, lease = tenant_safe_payments_in_db
    client = auth_client_factory(user_id=lease.tenant.user_id)
    limit = 2
    
    response = client.get(f'{payment_url}/me/{lease.id}?limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit

def test_tenant_get_own_lease_payments_pagination_skip(auth_client_factory, tenant_safe_payments_in_db):
    """
    Verifies that the skip parameter correctly offsets personal payments.
    """
    db_payments, lease = tenant_safe_payments_in_db
    client = auth_client_factory(user_id=lease.tenant.user_id)
    skip = 1
    limit = 3
    
    response = client.get(f'{payment_url}/me/{lease.id}?skip={skip}&limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit
    assert data[0]['id'] == db_payments[skip].id

def test_tenant_get_payments_lease_does_not_exist_returns_404(authenticated_tenant_client):
    """
    Tests that tenant getting payments for non-existent lease returns 404.
    """
    fake_lease_id = 9999
    response = authenticated_tenant_client.get(f'{payment_url}/me/{fake_lease_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

def test_tenant_get_other_tenants_payments_returns_404(auth_client_factory, add_second_tenant_to_db, multiple_safe_payments_in_db):
    """
    Tests that a tenant cannot fetch payments for a lease they do not own.
    """
    db_payments, lease = multiple_safe_payments_in_db
    
    # Authenticate as a completely different tenant
    client = auth_client_factory(user_id=add_second_tenant_to_db.user_id)
    
    response = client.get(f'{payment_url}/me/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lease could not be found'

def test_landlord_cannot_hit_tenant_payments_endpoint_returns_403(authenticated_landlord_client, multiple_safe_payments_in_db):
    """
    Tests that a landlord cannot access the tenant's payment history endpoint.
    """
    db_payments, lease = multiple_safe_payments_in_db
    response = authenticated_landlord_client.get(f'{payment_url}/me/{lease.id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only tenants are allowed.'
