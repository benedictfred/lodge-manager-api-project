import time

import pytest
from fastapi import status

from app.core.enums import TenantStatus
from test.conftest import mock_landlord_schema, base_url

auth_url_base = f'{base_url}/auth'

def test_register_landlord_returns_201(client, mock_landlord_schema):
    """
    Tests that a landlord can be registered and returns a 201 status code.
    """
    landlord_schema = mock_landlord_schema

    response = client.post(f'{auth_url_base}/register/landlord', json=landlord_schema.model_dump())
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED

    assert data['first_name']  == landlord_schema.first_name
    assert data['email'] == landlord_schema.email
    assert data['last_name'] == landlord_schema.last_name
    assert data['phone_no'] == landlord_schema.phone_no

    assert 'id' in data
    assert 'password' not in data



def test_register_existing_user_returns_400(client, add_landlord_to_db, mock_landlord_schema):
    """
    Tests that registering an existing user returns a 400 status code.
    """
    l_schema = mock_landlord_schema
    response = client.post(f'{auth_url_base}/register/landlord', json=l_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert data['detail'] == f'User: {add_landlord_to_db.email} already exists'



def test_login_user_returns_200(client, add_landlord_to_db, mock_landlord_schema):
    """
    Tests that a user can log in and returns a 200 status code.
    """
    l_schema = mock_landlord_schema
    payload = {
        'username': l_schema.email,
        'password': l_schema.password
    }
    response = client.post(f'{auth_url_base}/login', data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert data['id'] == add_landlord_to_db.id
    assert data['role'] == 'Landlord'

@pytest.mark.parametrize("username, password, error_detail, needs_db_user", [
    # Case 1: The user does NOT exist in the database. No fixture needed.
    ("non_existent_user@test.com", "any_password", "Invalid email or password.", False),

    # Case 2: The user DOES exist, but the password is wrong. Fixture is needed.
    ("landlord@test.com", "wrong_password", "Invalid email or password.", True),
])
def test_login_with_invalid_credentials_returns_401(client, username, password, error_detail, needs_db_user, add_landlord_to_db):
    """
    Tests that login fails with a 401 status code for various invalid credential combinations.
    """
    # If this specific test run needs a user in the DB, we use the email from the fixture.
    # Otherwise, we use the email provided in the parameters.
    login_username = add_landlord_to_db.email if needs_db_user else username

    payload = {
        'username': login_username,
        'password': password
    }
    response = client.post(f'{auth_url_base}/login', data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert data['detail'] == error_detail


def test_register_user_with_case_insensitive_duplicate_email_returns_400(client, add_landlord_to_db, mock_landlord_schema):
    """
    Tests that a user cannot register with an email that already exists, regardless of case.
    """
    existing_user_email = add_landlord_to_db.email

    duplicate_schema = mock_landlord_schema
    duplicate_schema.email = existing_user_email.upper()

    response = client.post(f'{auth_url_base}/register/landlord', json=duplicate_schema.model_dump())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == f'User: {add_landlord_to_db.email} already exists'

def test_register_tenant_returns_201(client, mock_tenant_schema, add_lodge_to_db):
    """
    Tests that a tenant can be registered and returns a 201 status code.
    """
    t_payload = mock_tenant_schema.model_dump(mode='json')

    response = client.post(f'{auth_url_base}/register/tenant', json=t_payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data['tenant_type'] == mock_tenant_schema.tenant_info.tenant_type
    assert data['emergency_contact_name'] == mock_tenant_schema.tenant_info.emergency_contact_name
    assert data['emergency_contact_phone_no'] == mock_tenant_schema.tenant_info.emergency_contact_phone_no
    assert data['status'] == TenantStatus.PENDING
    assert 'id' in data
    assert 'user_id' in data
    assert data['user'] != {}




def test_get_me_returns_authenticated_user(authenticated_landlord_client, add_landlord_to_db):

    response = authenticated_landlord_client.get(f'{auth_url_base}/me')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data['id'] == add_landlord_to_db.id
    assert data['role'] == 'Landlord'

def test_get_me_not_token_returns_401(client):
    response = client.get(f'{auth_url_base}/me')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_me_not_exist_returns_404(test_db, authenticated_landlord_client, add_landlord_to_db):
    test_db.delete(add_landlord_to_db)
    test_db.commit()

    response = authenticated_landlord_client.get(f'{auth_url_base}/me')
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_logout_authenticated_user_returns_200(authenticated_landlord_client):
    response = authenticated_landlord_client.post(f'{auth_url_base}/logout')

    assert response.status_code == status.HTTP_200_OK
    cookies = response.headers.get('set-cookie')

    assert 'access_token=""' in cookies
    assert 'refresh_token=""' in cookies
    assert 'Max-Age' in cookies


def test_refresh_stolen_refresh_token_for_logged_out_user_returns_401(authenticated_landlord_client):
    authenticated_landlord_client.post(f'{auth_url_base}/logout')

    response = authenticated_landlord_client.post(f'{auth_url_base}/refresh')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_rotation_blocks_stolen_token(authenticated_landlord_client):
    # 1. Capture the FIRST (original) refresh token
    first_refresh_token = authenticated_landlord_client.cookies.get('refresh_token')

    time.sleep(1)

    # 2. Hit /refresh. This will delete the first token from the DB and give the client a NEW token.
    response1 = authenticated_landlord_client.post(f'{auth_url_base}/refresh')
    assert response1.status_code == status.HTTP_200_OK

    # 3. Simulate a hacker trying to use the FIRST token that they stole earlier
    # We pass the cookies dictionary directly to override the client's internal cookie jar for this request
    response2 = authenticated_landlord_client.post(
        f'{auth_url_base}/refresh',
        cookies={"refresh_token": first_refresh_token}
    )

    # 4. Prove the database blocked it because it was deleted during the rotation in Step 2
    assert response2.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_while_not_logged_in_returns_401(client):
    response = client.post(f'{auth_url_base}/logout')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
