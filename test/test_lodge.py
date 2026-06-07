
from fastapi import status


def test_landlord_register_lodge_returns_200(authenticated_landlord_client,mock_landlord_schema, mock_lodge_schema):
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post('/api/v1/lodges/register', json=payload)
    data = response.json()

    assert  response.status_code == status.HTTP_200_OK
    assert data['name'] == mock_lodge_schema.name
    assert data['address'] == mock_lodge_schema.address
    assert 'id' in data
    assert 'landlord_id' in data


def test_register_duplicate_lodge_returns_400(authenticated_landlord_client, add_lodge_to_db, mock_lodge_schema):
    payload = mock_lodge_schema.model_dump()

    response = authenticated_landlord_client.post('/api/v1/lodges/register', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert data['detail'] == f'Lodge: {mock_lodge_schema.name} already exists'


