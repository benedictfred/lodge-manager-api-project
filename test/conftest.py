import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.api.deps import get_db
from app.core.enums import StudentLevel, TenantType
from app.main import app
from app.db.session import Base
from fastapi.testclient import TestClient
from app.schemas import user as schema_user
from app.services import user_service, lodge_service
from app.schemas import tenantprofile as schema_tenant
from app.schemas import lodge as schema_lodge

SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args= {'check_same_thread': False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)



@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_landlord_client(auth_client_factory, add_landlord_to_db, mock_landlord_schema):
    l_schema = mock_landlord_schema

    client = auth_client_factory(email=l_schema.email, password=l_schema.password)
    return client

@pytest.fixture
def auth_client_factory(client):
    def _authenticate(email:str, password:str):

        payload = {
            'username': email,
            'password': password
        }
        response = client.post('/api/v1/auth/login', data=payload)
        print(response)
        token = response.json()['access_token']

        client.headers = {
            'Authorization': f'Bearer {token}'
        }

        return client

    return _authenticate


@pytest.fixture
def mock_landlord_schema():
    return schema_user.UserCreate(first_name='Landlord', last_name='A',
                                  email='landlord@test.com', password='Landlord12345', phone_no='08108417160')



@pytest.fixture
def mock_tenant_user_schema():
    return schema_user.UserCreate(first_name='Tenant', last_name='A',
                                  email='tenant@test.com', password='Tenant12345', phone_no='08108417160')

@pytest.fixture
def mock_lodge_schema():
    return schema_lodge.LodgeCreate(name='East Lagon', address='Ifite, teezers')



@pytest.fixture
def mock_tenant_schema(mock_tenant_user_schema):
    return schema_tenant.TenantProfileCreate(
        user_info=mock_tenant_user_schema,
        tenant_info=schema_tenant.TenantBase(
            lodge_id=1,
            level=StudentLevel.LEVEL_200,
            tenant_type=TenantType.STUDENT,
            emergency_contact_name='mrs bond',
            emergency_contact_phone_no='0834124859',
            reg_no=298456718495


        )
    )


@pytest.fixture
def add_landlord_to_db(test_db, mock_landlord_schema):
    l_schema = mock_landlord_schema
    return user_service.sign_up_landlord(test_db, landlord_data=l_schema)




@pytest.fixture
def add_lodge_to_db(authenticated_landlord_client, test_db, add_landlord_to_db, mock_lodge_schema):
    lodge_service.create_new_loge_for_landlord(test_db,landlord_id= add_landlord_to_db.id, lodge_in=mock_lodge_schema)
