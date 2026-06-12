import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import random
from datetime import date, timedelta

from app.api.deps import get_db
from app.core import security
from app.core.enums import StudentLevel, TenantType, RoomStatus
from app.main import app
from app.db.session import Base
from fastapi.testclient import TestClient
from app.schemas import user as schema_user
from app.services import user_service, lodge_service, tenant_services, room_service, lease_services
from app.schemas import tenantprofile as schema_tenant
from app.schemas import lodge as schema_lodge
from app.schemas import room as schema_room
from app.schemas import lease as schema_lease

SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL,
    connect_args= {'check_same_thread': False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture
def test_db():
    """
    A pytest fixture that sets up a test database.
    It creates all tables before the test and drops them after the test.
    """
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
    """
    A pytest fixture that provides a TestClient for the FastAPI application.
    It overrides the `get_db` dependency to use the test database.
    """
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_landlord_client(auth_client_factory, add_landlord_to_db, mock_landlord_schema):
    """
    A pytest fixture that provides an authenticated client for a landlord.
    """
    landlord  = add_landlord_to_db

    client = auth_client_factory(user_id=landlord.id)
    client.landlord = landlord

    return client


@pytest.fixture
def auth_client_factory(client):
    """
    A pytest fixture that provides a factory for creating authenticated clients.
    """
    def _authenticate(user_id: int):


        token = security.create_access_token(subject=user_id)

        client.headers = {
            'Authorization': f'Bearer {token}'
        }

        return client

    return _authenticate


@pytest.fixture
def landlord_schema_factory():
    """
    A pytest fixture that provides a factory for creating landlord schemas.
    """
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
    """
    A pytest fixture that provides a mock landlord schema.
    """
    return landlord_schema_factory()





@pytest.fixture
def mock_lodge_schema(lodge_schema_factory):
    """
    A pytest fixture that provides a mock lodge schema.
    """
    return lodge_schema_factory()

@pytest.fixture
def mock_update_lodge_schema():
    """
    A pytest fixture that provides a mock lodge update schema.
    """
    return schema_lodge.LodgeUpdate(
        name='A Lodge',
        address='A Address'
    )

@pytest.fixture
def tenant_schema_factory(add_lodge_to_db):
    """
    A pytest fixture that provides a factory for creating tenant schemas.
    """
    def _create(
            first_name: str = 'Tenant',
            last_name: str = 'A',
            email: str = 'tenant@test.com',
            lodge_id: int = add_lodge_to_db.id,
            level: StudentLevel = StudentLevel.LEVEL_200,
            tenant_type: TenantType = TenantType.STUDENT
    ):
        user_info = schema_user.UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password='Tenant12345',
            phone_no='08108417160'
        )
        return schema_tenant.TenantProfileCreate(
            user_info=user_info,
            tenant_info=schema_tenant.TenantBase(
                lodge_id=lodge_id,
                level=level,
                tenant_type=tenant_type,
                emergency_contact_name='mrs bond',
                emergency_contact_phone_no='0834124859',
                reg_no=random.randint(1000000, 9999999)
            )
        )
    return _create

#a factory fixture for creating a tenant in a lodge

@pytest.fixture
def mock_tenant_schema(tenant_schema_factory):
    """
    A pytest fixture that provides a mock tenant schema.
    """
    return tenant_schema_factory()

@pytest.fixture
def room_schema_factory(add_lodge_to_db):
    """
    A pytest fixture that provides a factory for creating room schemas.
    """
    def _create(
            room_no: str = 'Test Rm-1',
            description: str = 'spacious self con',
            base_rent_price: int = 210000,
            status: RoomStatus = RoomStatus.VACANT,
            lodge_id: int = add_lodge_to_db.id

    ):
        return schema_room.RoomCreate(
            room_no=room_no,
            description=description,
            base_rent_price=base_rent_price,
            status=status,
            lodge_id=lodge_id
        )

    return _create

@pytest.fixture
def mock_room_schema(room_schema_factory):
    """
    A pytest fixture that provides a mock room schema.
    """
    return room_schema_factory()

@pytest.fixture
def mock_update_room_schema():
    """
    A pytest fixture that provides a mock room update schema.
    """
    return schema_room.RoomUpdate(
        room_no= 'Rm-1 Test',
        description= 'Upstairs, 2nd floor',
        base_rent_price= 400000,
        status= RoomStatus.MAINTENANCE
    )

@pytest.fixture
def lodge_schema_factory():
    """
    A pytest fixture that provides a factory for creating lodge schemas.
    """
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
    """
    A pytest fixture that adds a landlord to the database.
    """
    l_schema = mock_landlord_schema
    return user_service.sign_up_landlord(test_db, landlord_data=l_schema)


@pytest.fixture
def add_different_landlord(test_db, landlord_schema_factory):
    """
    A pytest fixture that adds a different landlord to the database.
    """
    new_l_schema = landlord_schema_factory(first_name='Landlord', last_name='B', email='landlordb@test.com',
                                           password='Landlordb12345', phone_no='091580380375')
    return user_service.sign_up_landlord(test_db, landlord_data=new_l_schema)

@pytest.fixture
def add_lodge_to_db(test_db, add_landlord_to_db, mock_lodge_schema):
    """
    A pytest fixture that adds a lodge to the database.
    """
    return lodge_service.create_new_lodge_for_landlord(test_db, landlord_id= add_landlord_to_db.id, lodge_in=mock_lodge_schema)

@pytest.fixture
def add_diff_landlord_lodge(test_db, add_different_landlord, lodge_schema_factory):
    """
    A pytest fixture that adds a lodge for a different landlord to the database.
    """
    lodge_schema = lodge_schema_factory(name='Lodge A', address='Address A')
    return lodge_service.create_new_lodge_for_landlord(test_db, landlord_id=add_different_landlord.id, lodge_in=lodge_schema)

@pytest.fixture
def lodges_in_db(test_db, add_landlord_to_db, lodge_schema_factory):
    """
    A pytest fixture that adds multiple lodges to the database.
    """

    db_lodges: list[schema_lodge.LodgeResponse] = []
    for i in range(4):
        lodge_schema = lodge_schema_factory(name=f'Lodge {i + 1}', address=f'Address {i + 1}')
        new_lodge = lodge_service.create_new_lodge_for_landlord(test_db, landlord_id=add_landlord_to_db.id,
                                                                lodge_in=lodge_schema)
        db_lodges.append(new_lodge)

    return db_lodges

@pytest.fixture
def rooms_in_lodge(test_db,room_schema_factory, add_landlord_to_db, add_lodge_to_db):
    """
    A pytest fixture that adds multiple rooms to a lodge in the database.
    """
    max_rooms = 50
    rooms_in_db = []
    for i in range(max_rooms):
        rm_schema = room_schema_factory(
            room_no=f'Test rm{i + 1}',
            description=f'description Test {i + 1}',
            base_rent_price= random.randint(250000, 350000),
            status= RoomStatus.VACANT,
            lodge_id=add_lodge_to_db.id
        )
        new_room = room_service.create_room_for_lodge(test_db, landlord_id=add_landlord_to_db.id, room_in=rm_schema)
        rooms_in_db.append(new_room)

    return rooms_in_db

@pytest.fixture
def tenants_in_db(test_db, tenant_schema_factory, add_lodge_to_db):
    """
    A pytest fixture that adds multiple tenants to the database in a specific lodge.
    """
    max_tenants = 10
    db_tenants = []
    for i in range(max_tenants):
        t_schema = tenant_schema_factory(
            first_name=f'TenantFirst{i + 1}',
            last_name=f'TenantLast{i + 1}',
            email=f'tenant{i + 1}@test.com',
            lodge_id=add_lodge_to_db.id
        )
        new_tenant = tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)
        db_tenants.append(new_tenant)

    return db_tenants

@pytest.fixture
def add_tenant_to_db(test_db, mock_tenant_schema, add_lodge_to_db):
    """
    A pytest fixture that adds a tenant to the database.
    """
    t_schema = mock_tenant_schema
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)


@pytest.fixture
def add_room_to_db(test_db, mock_room_schema, add_landlord_to_db):
    """
    A pytest fixture that adds a room to the database.
    """
    return room_service.create_room_for_lodge(test_db, room_in=mock_room_schema, landlord_id=add_landlord_to_db.id)
    
@pytest.fixture
def add_diff_landlord_room(test_db, room_schema_factory, add_different_landlord, add_diff_landlord_lodge):
    """
    A pytest fixture that adds a room belonging to a different landlord.
    """
    rm_schema = room_schema_factory(lodge_id=add_diff_landlord_lodge.id)
    return room_service.create_room_for_lodge(test_db, landlord_id=add_different_landlord.id, room_in=rm_schema)

@pytest.fixture
def authenticated_tenant_client(auth_client_factory, add_tenant_to_db):
    """
    A pytest fixture that provides an authenticated client for a tenant.
    """
    tenant = add_tenant_to_db
    client = auth_client_factory(user_id=tenant.user_id)
    client.tenant = tenant
    return client

@pytest.fixture
def add_second_tenant_to_db(test_db, tenant_schema_factory, add_lodge_to_db):
    """
    A pytest fixture that adds a second tenant to the same lodge.
    """
    t_schema = tenant_schema_factory(email="tenant2@test.com", first_name="TenantB")
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)

@pytest.fixture
def add_diff_landlord_tenant(test_db, tenant_schema_factory, add_diff_landlord_lodge):
    """
    A pytest fixture that adds a tenant to a different landlord's lodge.
    """
    t_schema = tenant_schema_factory(lodge_id=add_diff_landlord_lodge.id, email="tenant3@test.com")
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)

@pytest.fixture
def lease_schema_factory(add_tenant_to_db, add_room_to_db):
    """
    A pytest fixture that provides a factory for creating LeaseCreate schemas.
    """
    def _create(
        tenant_id: int = add_tenant_to_db.id,
        room_id: int = add_room_to_db.id,
        agreed_rent_amt: int = 210000,
        total_amt_paid: int = 105000,
        start_date: date = date.today(),
        end_date: date = date.today() + timedelta(days=365)
    ):
        return schema_lease.LeaseCreate(
            tenant_id=tenant_id,
            room_id=room_id,
            agreed_rent_amt=agreed_rent_amt,
            total_amt_paid=total_amt_paid,
            start_date=start_date,
            end_date=end_date
        )
    return _create

@pytest.fixture
def mock_lease_schema(lease_schema_factory):
    """
    A pytest fixture that provides a mock lease schema using the lease_schema_factory.
    """
    return lease_schema_factory()

@pytest.fixture
def add_active_lease_to_db_direct(test_db, mock_lease_schema, add_landlord_to_db):
    """
    Fixture to create and add an active lease to the database directly via the service.
    """
    return lease_services.create_new_lease(
        db=test_db,
        lease_data=mock_lease_schema,
        landlord_user=add_landlord_to_db
    )