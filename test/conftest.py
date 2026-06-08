import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.api.deps import get_db
from app.core import security
from app.core.enums import StudentLevel, TenantType
from app.main import app
from app.db.session import Base
from fastapi.testclient import TestClient
from app.schemas import user as schema_user
from app.services import user_service, lodge_service, tenant_services
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

base_url = "/api/v1"

@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_landlord_client(auth_client_factory, add_landlord_to_db, mock_landlord_schema):
    landlord  = add_landlord_to_db

    client = auth_client_factory(user_id=landlord.id)
    client.landlord = landlord

    return client


@pytest.fixture
def auth_client_factory(client):
    def _authenticate(user_id: int):


        token = security.create_access_token(subject=user_id)

        client.headers = {
            'Authorization': f'Bearer {token}'
        }

        return client

    return _authenticate


@pytest.fixture
def landlord_schema_factory():
    def _create(
            first_name: str = 'Landlord A',
            last_name: str = 'Test',
            email: str = 'landlord@test.com',
            password: str = 'Landlord12345',
            phone_no: str = '08108417160'
    ):
        return schema_user.UserCreate(first_name=first_name, last_name=last_name,
                               email=email, password=password, phone_no=phone_no)

    return _create


@pytest.fixture
def mock_landlord_schema(landlord_schema_factory):
    return landlord_schema_factory()



@pytest.fixture
def mock_tenant_user_schema():
    return schema_user.UserCreate(first_name='Tenant', last_name='A',
                                  email='tenant@test.com', password='Tenant12345', phone_no='08108417160')

@pytest.fixture
def mock_lodge_schema(lodge_schema_factory):
    return lodge_schema_factory()

@pytest.fixture
def mock_update_lodge_schema():
    return schema_lodge.LodgeUpdate(
        name='A Lodge',
        address='A Address'
    )
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
def room_schema_factory():
    def _create(
            room_no: str,

    )

@pytest.fixture
def mock_room_schema():
    pass

@pytest.fixture
def lodge_schema_factory():
    def _create(
            name: str = 'Lodge Test',
            address: str = 'Test Address'
    ):
        return schema_lodge.LodgeCreate(
            name=name, address=address
        )
    return _create

@pytest.fixture
def add_landlord_to_db(test_db, mock_landlord_schema):
    l_schema = mock_landlord_schema
    return user_service.sign_up_landlord(test_db, landlord_data=l_schema)


@pytest.fixture
def add_different_landlord(test_db, landlord_schema_factory):
    new_l_schema = landlord_schema_factory(first_name='Landlord', last_name='B', email='landlordb@test.com',
                                           password='Landlordb12345', phone_no='091580380375')
    return user_service.sign_up_landlord(test_db, landlord_data=new_l_schema)

@pytest.fixture
def add_lodge_to_db(test_db, add_landlord_to_db, mock_lodge_schema):
    return lodge_service.create_new_lodge_for_landlord(test_db, landlord_id= add_landlord_to_db.id, lodge_in=mock_lodge_schema)

@pytest.fixture
def add_diff_landlord_lodge(test_db, add_different_landlord, lodge_schema_factory):
    lodge_schema = lodge_schema_factory(name='Lodge A', address='Address A')
    return lodge_service.create_new_lodge_for_landlord(test_db, landlord_id=add_different_landlord.id, lodge_in=lodge_schema)

@pytest.fixture
def lodges_in_db(test_db, add_landlord_to_db):

    db_lodges: list[schema_lodge.LodgeResponse] = []
    for i in range(4):
        lodge_schema = schema_lodge.LodgeCreate(name=f'Lodge {i + 1}', address=f'Address {i + 1}')
        new_lodge = lodge_service.create_new_lodge_for_landlord(test_db, landlord_id=add_landlord_to_db.id,
                                                                lodge_in=lodge_schema)
        db_lodges.append(new_lodge)

    return db_lodges


@pytest.fixture
def tenants_in_db(test_db, add_landlord_to_db):
    pass

@pytest.fixture
def add_tenant_to_db(test_db, mock_tenant_schema, add_lodge_to_db):
    t_schema = mock_tenant_schema
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)



@pytest.fixture
def authenticated_tenant_client(auth_client_factory, add_tenant_to_db):
    return auth_client_factory(user_id=add_tenant_to_db.user_id)