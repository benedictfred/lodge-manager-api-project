import pytest
from fastapi import status

from test.conftest import base_url, add_lodge_to_db
from test.test_room import room_url

lodge_url = f'{base_url}/lodges'

def test_landlord_register_lodge_returns_200(authenticated_landlord_client, mock_lodge_schema):
    """
    Tests that a landlord can register a lodge and returns a 200 status code.
    """
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert  response.status_code == status.HTTP_200_OK
    assert data['name'] == mock_lodge_schema.name
    assert data['address'] == mock_lodge_schema.address
    assert 'id' in data
    assert 'landlord_id' in data

#not going to test this bcz none of my schema rules have been set , -a later todo
# @pytest.mark.parametrize("invalid_payload, expected_detail_part", [
#     ({"address": "Some Address"}, "Field required"),  # Missing name
#     ({"name": "Some Name"}, "Field required"),  # Missing address
#     ({"name": "", "address": "Some Address"}, "String should have at least 1 character"),
#     ({"name": "   ", "address": "Some Address"}, "String should have at least 1 character"),
# ])
# def test_register_lodge_with_invalid_data_returns_422(authenticated_landlord_client, invalid_payload,
#                                                       expected_detail_part):
#     """Tests that creating a lodge with invalid or missing data fails."""
#     response = authenticated_landlord_client.post(f'{lodge_url}/register', json=invalid_payload)
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#     assert expected_detail_part in str(response.json())


def test_register_duplicate_lodge_returns_400(authenticated_landlord_client, add_lodge_to_db, mock_lodge_schema):
    """
    Tests that registering a duplicate lodge returns a 400 status code.
    """
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['detail'] == f'Lodge: {mock_lodge_schema.name} already exists'



def test_tenant_cannot_register_lodge_returns_403(authenticated_tenant_client,  mock_lodge_schema):
    """
    Tests that a tenant cannot register a lodge and returns a 403 status code.
    """
    payload = mock_lodge_schema.model_dump()

    response = authenticated_tenant_client.post(f'{lodge_url}/register', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == f'Only landlords are allowed.'


def test_landlord_get_lodge_by_id_returns_200(authenticated_landlord_client, add_lodge_to_db):
    """
    Tests that a landlord can get a lodge by ID and returns a 200 status code.
    """
    response = authenticated_landlord_client.get(f'{lodge_url}/{authenticated_landlord_client.landlord.id}')

    data = response.json()

    assert  response.status_code == status.HTTP_200_OK
    assert data['name'] == add_lodge_to_db.name
    assert data['address'] == add_lodge_to_db.address
    assert data['id'] == add_lodge_to_db.id
    assert  data['landlord_id'] == add_lodge_to_db.landlord_id
    assert data['is_active'] == add_lodge_to_db.is_active

def test_landlord_get_lodge_id_not_exist_returns_404(authenticated_landlord_client, add_landlord_to_db):
    """
    Tests that getting a lodge with a non-existent ID returns a 404 status code.
    """
    fake_lodge_id = 2
    response = authenticated_landlord_client.get(f'{lodge_url}/{fake_lodge_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert  data['detail'] == 'Lodge could not be found'

def test_landlord_get_lodge_not_owned_returns_404(authenticated_landlord_client, add_diff_landlord_lodge):
    """
    Tests that a landlord cannot get a lodge they do not own and returns a 404 status code.
    """
    response = authenticated_landlord_client.get(f'{lodge_url}/{add_diff_landlord_lodge.id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'



def test_get_landlord_lodges_returns_200(authenticated_landlord_client, lodges_in_db):
    """
    Tests that a landlord can get a list of their lodges and returns a 200 status code.
    """
    response = authenticated_landlord_client.get(f'{lodge_url}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(lodges_in_db)


@pytest.mark.parametrize("update_payload, expected_name, expected_address", [
    # Scenario 1: Update name only
    ({"name": "New Lodge Name"}, "new lodge name", "test address"),
    # Scenario 2: Update address only
    ({"address": "New Lodge Address"}, "lodge test", "New Lodge Address"),
    # Scenario 3: Update both name and address
    ({"name": "Updated Name", "address": "Updated Address"}, "updated name", "Updated Address"),
])
def test_landlord_update_lodge_scenarios(
    authenticated_landlord_client,
    add_lodge_to_db,
    update_payload,
    expected_name,
    expected_address
):
    """
    Tests various valid scenarios for updating a lodge.
    """
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.patch(f'{lodge_url}/{lodge_id}', json=update_payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == expected_name.lower()
    assert data['address'] == expected_address.lower()
    assert data['id'] == lodge_id
    assert data['landlord_id'] == add_lodge_to_db.landlord_id


def test_landlord_update_non_existent_lodge_returns_404(authenticated_landlord_client, mock_update_lodge_schema):
    """
    Tests that a landlord cannot update a non-existent lodge.
    """
    fake_lodge_id = 9999
    response = authenticated_landlord_client.patch(f'{lodge_url}/{fake_lodge_id}', json=mock_update_lodge_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'


def test_landlord_update_lodge_not_owned_returns_404(authenticated_landlord_client, add_diff_landlord_lodge, mock_update_lodge_schema):
    """
    Tests that a landlord cannot update a lodge owned by another landlord.
    """
    response = authenticated_landlord_client.patch(f'{lodge_url}/{add_diff_landlord_lodge.id}', json=mock_update_lodge_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'


def test_landlord_get_paginated_tenants_returns_200(authenticated_landlord_client, tenants_in_db, add_lodge_to_db):
    """
    Tests that a landlord can get a paginated list of tenants in their lodge.
    """
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lodge_url}/{lodge_id}/tenants') # Assuming /tenants/ endpoint for listing
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(tenants_in_db) # Should return all if no limit/skip specified


def test_landlord_get_tenants_pagination_limit(authenticated_landlord_client,add_landlord_to_db, tenants_in_db):
    """Verifies that the limit parameter restricts the number of returned tenants."""
    limit = 5
    lodge_id = add_landlord_to_db.id
    response = authenticated_landlord_client.get(f'{lodge_url}/{lodge_id}/tenants?limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit
    # Ensure the first tenant is the first one from the fixture
    assert data[0]['user']['email'] == tenants_in_db[0].user.email


def test_landlord_get_tenants_pagination_skip(authenticated_landlord_client, tenants_in_db, add_lodge_to_db):
    """Verifies that the skip parameter correctly offsets the returned tenants."""
    skip = 2
    limit = 3
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lodge_url}/{lodge_id}/tenants?skip={skip}&limit={limit}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == limit
    # Ensure the first tenant in the response is the one after the skip
    assert data[0]['user']['email'] == tenants_in_db[skip].user.email


def test_landlord_get_tenants_pagination_skip_exceeds_total(authenticated_landlord_client, tenants_in_db,
                                                            add_lodge_to_db):
    """Verifies that skipping more tenants than exist returns an empty list."""
    total_tenants = len(tenants_in_db)
    lodge_id = add_lodge_to_db.id
    response = authenticated_landlord_client.get(f'{lodge_url}/{lodge_id}/tenants?skip={total_tenants + 5}&limit=5')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0

def test_landlord_get_tenants_from_non_existent_lodge_returns_404(authenticated_landlord_client):
    """
    Tests that a landlord cannot get tenants from a lodge that does not exist.
    """
    fake_lodge_id = 9999
    response = authenticated_landlord_client.get(f'{lodge_url}/{fake_lodge_id}/tenants')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'

def test_landlord_create_lodge_with_rooms(authenticated_landlord_client,
                                          lodge_schema_with_room_generator_factory):

    lodge_schema = lodge_schema_with_room_generator_factory()
    response = authenticated_landlord_client.post(f'{lodge_url}/register', json=lodge_schema.model_dump())
    data = response.json()
    assert response.status_code == status.HTTP_200_OK

    assert data['name'] == lodge_schema.name
    assert data['address'] == lodge_schema.address
    assert 'id' in data
    assert 'landlord_id' in data

    lodge_id = data['id']
    response2 = authenticated_landlord_client.get(f'{room_url}/{lodge_id}/rooms')

    assert response2.status_code == status.HTTP_200_OK
    data = response2.json()
    assert len(data) == 5