
from fastapi import status

from test.conftest import base_url

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
    print(data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'



def test_get_landlord_lodges_returns_200(authenticated_landlord_client, lodges_in_db):
    """
    Tests that a landlord can get a list of their lodges and returns a 200 status code.
    """
    response = authenticated_landlord_client.get(f'{lodge_url}')
    data = response.json()
    print(data)
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(lodges_in_db)


def test_landlord_update_lodge_address_by_id_returns_200(authenticated_landlord_client, add_lodge_to_db, mock_update_lodge_schema):
    """
    Tests that a landlord can update a lodge's address by ID and returns a 200 status code.
    """
    update_payload = mock_update_lodge_schema.model_dump(exclude='name')
    response = authenticated_landlord_client.patch(url=f'{lodge_url}/{add_lodge_to_db.id}', json=update_payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['address'] == mock_update_lodge_schema.address.lower()