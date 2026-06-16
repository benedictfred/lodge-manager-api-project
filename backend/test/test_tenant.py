import pytest
from fastapi import status

from app.crud.lease import crud_lease
from app.crud.tenantprofile import crud_tenant
from app.services import lease_services
from test.conftest import base_url, test_db

tenant_url = f'{base_url}/tenants'


def test_tenant_get_personal_details_returns_200(authenticated_tenant_client, add_tenant_to_db):
    """
    Tests that a tenant can retrieve their own personal details.
    """
    response = authenticated_tenant_client.get(f'{tenant_url}/profile')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['id'] == add_tenant_to_db.id
    assert data['user_id'] == add_tenant_to_db.user_id
    assert data['tenant_type'] == add_tenant_to_db.tenant_type


def test_mock_get_tenant_history(test_db, add_tenant_to_db, tenant_lease_history_in_db):
    db_items = lease_services.get_filtered_leases_tenant(test_db, tenant_profile=add_tenant_to_db)
    print(db_items)

@pytest.mark.parametrize("update_payload, field_to_check, expected_value", [
    ({'user_info': {"first_name": "John"}}, "first_name", "John"),
    ({'user_info': {"last_name": "Doe"}}, "last_name", "Doe"),
    ({'user_info': {"phone_no": "1234567890"}}, "phone_no", "1234567890"),
    ({'tenant_info': {"emergency_contact_name": "Jane Doe"}}, "emergency_contact_name", "Jane Doe"),
    ({'tenant_info': {"emergency_contact_phone_no": "0987654321"}}, "emergency_contact_phone_no", "0987654321"),
])
def test_tenant_can_update_own_profile_returns_200(authenticated_tenant_client, update_payload, field_to_check,
                                                   expected_value):
    """
    Tests that a tenant can update their own core profile details.
    """

    response = authenticated_tenant_client.patch(f'{tenant_url}/profiles/me', json=update_payload)
    data = response.json()


    assert response.status_code == status.HTTP_200_OK

    normalized_expected_value = expected_value.lower() if isinstance(expected_value, str) else expected_value

    if field_to_check not in data and 'user' in data:
        actual_data_value = data['user'].get(field_to_check)
        assert actual_data_value == normalized_expected_value
    else:
        actual_data_value = data.get(field_to_check)
        assert actual_data_value == normalized_expected_value


def test_tenant_get_other_tenant_profile_returns_403(authenticated_tenant_client, add_second_tenant_to_db):
    """
    Tests that a tenant cannot get another tenant's profile details.
    """
    response = authenticated_tenant_client.get(f'{tenant_url}/profile/{add_second_tenant_to_db.id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'


def test_landlord_get_tenant_profile_returns_200(authenticated_landlord_client, add_tenant_to_db):
    """
    Tests that a landlord can get the profile of a tenant in their lodge.
    """
    response = authenticated_landlord_client.get(f'{tenant_url}/profile/{add_tenant_to_db.id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['id'] == add_tenant_to_db.id
    assert data['user_id'] == add_tenant_to_db.user_id
    assert data['tenant_type'] == add_tenant_to_db.tenant_type


def test_landlord_get_tenant_profile_wrong_lodge_returns_404(authenticated_landlord_client, add_diff_landlord_tenant):
    """
    Tests that a landlord cannot get a tenant profile not belonging to his lodge.
    """
    response = authenticated_landlord_client.get(f'{tenant_url}/profile/{add_diff_landlord_tenant.id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'User could not be found'


def test_landlord_get_non_existing_tenant_profile_returns_404(authenticated_landlord_client):
    fake_tenant_id = 999
    response = authenticated_landlord_client.get(f'{tenant_url}/profile/{fake_tenant_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'User could not be found'


def test_landlord_cannot_hit_tenant_me_endpoint_returns_403(authenticated_landlord_client, add_tenant_to_db):
    """
    Tests that a landlord trying to access the tenant's '/profiles/me' endpoint is forbidden
    """

    update_payload = {"level": "LEVEL_300"}
    response = authenticated_landlord_client.patch(f'{tenant_url}/profiles/me', json=update_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['detail'] == 'Only tenants are allowed.'