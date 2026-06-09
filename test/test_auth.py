import pytest
from fastapi import status
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

    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


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
    t_payload = mock_tenant_schema.model_dump()

    response = client.post(f'{auth_url_base}/register/tenant', json=t_payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data['tenant_type'] == mock_tenant_schema.tenant_info.tenant_type
    assert data['emergency_contact_name'] == mock_tenant_schema.tenant_info.emergency_contact_name
    assert data['emergency_contact_phone_no'] == mock_tenant_schema.tenant_info.emergency_contact_phone_no
    assert 'id' in data
    assert 'user_id' in data
    assert data['user'] != {}


def test_register_tenant_lodge_not_exist_returns_404(client, mock_tenant_schema):
    """
    Tests that registering a tenant for a non-existent lodge returns a 404 status code.
    """
    t_payload = mock_tenant_schema.model_dump()

    response = client.post(f'{auth_url_base}/register/tenant', json=t_payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'