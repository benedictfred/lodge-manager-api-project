import pytest
from fastapi import status

from app.core.enums import RoomStatus
from test.conftest import base_url

room_url = f'{base_url}/rooms'


def test_landlord_create_room_returns_200(authenticated_landlord_client, mock_room_schema):
    """
    Tests that a landlord can create a room and returns a 200 status code.
    """
    response = authenticated_landlord_client.post(url=room_url, json=mock_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['room_no'] == mock_room_schema.room_no
    assert data['description'] == mock_room_schema.description
    assert data['base_rent_price'] == mock_room_schema.base_rent_price
    assert data['lodge_id'] == mock_room_schema.lodge_id
    assert 'id' in data
    assert 'created_at' in data


def test_create_duplicate_room_returns_400(authenticated_landlord_client, mock_room_schema, add_room_to_db):
    """
    Tests that creating a duplicate room returns a 400 status code.
    """
    response = authenticated_landlord_client.post(url=room_url, json=mock_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['detail'] == f'Room: {add_room_to_db.room_no} already exists'


def test_tenant_create_room_returns_403(authenticated_tenant_client, mock_room_schema):
    """
    Tests that a tenant cannot create a room and returns a 403 status code.
    """
    response = authenticated_tenant_client.post(url=room_url, json=mock_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'


def test_landlord_get_room_details_by_id_returns_200(authenticated_landlord_client, add_room_to_db):
    """
    Tests that a landlord can get room details by ID and returns a 200 status code.
    """
    response = authenticated_landlord_client.get(f'{room_url}/{add_room_to_db.id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['room_no'] == add_room_to_db.room_no
    assert data['description'] == add_room_to_db.description
    assert data['base_rent_price'] == add_room_to_db.base_rent_price
    assert data['lodge_id'] == add_room_to_db.lodge_id
    assert 'id' in data
    assert 'created_at' in data


def test_landlord_update_room_by_id_returns_200(authenticated_landlord_client, add_room_to_db, mock_update_room_schema):
    """
    Tests that a landlord can update a room by ID and returns a 200 status code.
    """
    response = authenticated_landlord_client.patch(url=f'{room_url}/{add_room_to_db.id}',
                                                   json=mock_update_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['room_no'] == mock_update_room_schema.room_no.lower()
    assert data['description'] == mock_update_room_schema.description.lower()
    assert data['base_rent_price'] == mock_update_room_schema.base_rent_price
    assert data['lodge_id'] == add_room_to_db.lodge_id

    assert 'id' in data
    assert 'created_at' in data


def test_landlord_update_non_existent_room_returns_404(authenticated_landlord_client, mock_update_room_schema):
    """
    Tests that updating a room that does not exist returns a 404 status code.
    """
    non_existent_room_id = 9999
    response = authenticated_landlord_client.patch(url=f'{room_url}/{non_existent_room_id}',
                                                   json=mock_update_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == f'Room could not be found'


def test_landlord_update_room_owned_by_another_landlord_returns_404(authenticated_landlord_client,
                                                                    add_diff_landlord_room, mock_update_room_schema):
    """
    Tests that a landlord cannot update a room owned by another landlord and returns a 404 status code.
    """
    response = authenticated_landlord_client.patch(url=f'{room_url}/{add_diff_landlord_room.id}',
                                                   json=mock_update_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == f'Room could not be found'


def test_tenant_update_room_by_id_returns_403(authenticated_tenant_client, add_room_to_db, mock_update_room_schema):
    """
    Tests that a tenant cannot update a room by ID and returns a 403 status code.
    """
    response = authenticated_tenant_client.patch(f'{room_url}/{add_room_to_db.id}',
                                                 json=mock_update_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'


def test_landlord_get_rooms_returns_200(authenticated_landlord_client, vacant_rooms_in_db):
    """
    Tests that a landlord can get a list of rooms and returns a 200 status code.
    """
    response = authenticated_landlord_client.get(url=room_url)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(vacant_rooms_in_db)


def test_get_rooms_pagination_limit(authenticated_landlord_client, vacant_rooms_in_db):
    """Verifies that the limit parameter restricts the number of returned items."""
    response = authenticated_landlord_client.get(f'{room_url}?limit=2')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2


def test_get_rooms_pagination_skip(authenticated_landlord_client, vacant_rooms_in_db):
    """Verifies that the skip parameter correctly offsets the returned items."""
    response = authenticated_landlord_client.get(f'{room_url}?skip=2&limit=1')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0]['room_no'] == vacant_rooms_in_db[2].room_no


def test_get_rooms_pagination_skip_exceeds_total(authenticated_landlord_client, vacant_rooms_in_db):
    """Verifies that skipping more items than exist returns an empty list."""
    total_rooms = len(vacant_rooms_in_db)
    response = authenticated_landlord_client.get(f'{room_url}?skip={total_rooms + 5}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 0

def test_tenant_cannot_create_room_returns_403(authenticated_tenant_client, mock_room_schema):
    """
    Tests that a tenant cannot create a room and returns a 403 status code.
    """
    response = authenticated_tenant_client.post(url=room_url, json=mock_room_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'


@pytest.mark.parametrize("update_fields", [
    {"room_no": "new-rm-101"},
    {"description": "updated description for testing"},
    {"base_rent_price": 500000},
    {"room_no": "rm-202", "base_rent_price": 350000},
    {"description": "luxury suite", "status": RoomStatus.MAINTENANCE}
])
def test_landlord_update_room_scenarios_returns_200(authenticated_landlord_client, add_room_to_db, update_fields):
    """
    Tests various scenarios for updating room details by a landlord.
    """
    response = authenticated_landlord_client.patch(
        url=f'{room_url}/{add_room_to_db.id}',
        json=update_fields
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    for key, value in update_fields.items():
        if isinstance(value, str):
            if isinstance(value, RoomStatus):
                assert data[key] == RoomStatus.MAINTENANCE
            else:
                assert data[key] == value.lower()
        else:
            assert data[key] == value

def test_tenant_cannot_update_room_returns_403(authenticated_tenant_client, add_room_to_db, mock_update_room_schema):
    """
    Tests that a tenant is forbidden from updating room details.
    """
    response = authenticated_tenant_client.patch(
        url=f'{room_url}/{add_room_to_db.id}',
        json=mock_update_room_schema.model_dump()
    )
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Only landlords are allowed.'
