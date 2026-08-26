

import pytest
from fastapi import status
from datetime import timedelta

from app.core.enums import LeaseStatus, InviteStatus, RoomStatus
from test.conftest import base_url

invite_url = f'{base_url}/invites'


def test_landlord_create_invite_record_returns_201(authenticated_landlord_client, invite_schema_factory, add_lodge_to_db, add_room_to_db):
    payload = invite_schema_factory(room_id=add_room_to_db.id, lodge_id=add_lodge_to_db.id).model_dump(mode='json')

    response = authenticated_landlord_client.post(f'{invite_url}', json=payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data['lodge_id'] == add_lodge_to_db.id
    assert data['room_id'] == add_room_to_db.id
    assert data['room_no'] == add_room_to_db.room_no
    assert data['status'] == InviteStatus.SENT


def test_landlord_get_invite_by_id_returns_200(authenticated_landlord_client, add_invite_to_db, add_lodge_to_db):
    invite_id = add_invite_to_db.id

    response = authenticated_landlord_client.get(f'{invite_url}/{invite_id}')
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data['lodge_name'] == add_lodge_to_db.name
    assert 'room_no' in data


def test_cannot_create_duplicate_active_invite_for_same_room_returns_400(authenticated_landlord_client, add_invite_to_db, invite_schema_factory):
    room_id = add_invite_to_db.room_id
    payload = invite_schema_factory(room_id=room_id, lodge_id=add_invite_to_db.lodge_id).model_dump(mode='json')

    response = authenticated_landlord_client.post(f'{invite_url}', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == "Room already has an active pending invitation."


def test_cannot_create_invite_for_diff_landlord_room_returns_404(authenticated_landlord_client, add_diff_landlord_room, invite_schema_factory):
    payload = invite_schema_factory(room_id=add_diff_landlord_room.id).model_dump(mode='json')

    response = authenticated_landlord_client.post(f'{invite_url}', json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_create_invite_for_maintenance_room_returns_400(authenticated_landlord_client, maintenance_rooms_in_db, invite_schema_factory):
    m_room = maintenance_rooms_in_db[0]
    payload = invite_schema_factory(room_id=m_room.id).model_dump(mode='json')

    response = authenticated_landlord_client.post(f'{invite_url}', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Maintenance" in response.json()['detail']



