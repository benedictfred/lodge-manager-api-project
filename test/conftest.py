import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import random
from datetime import date, timedelta

from app.api.deps import get_db
from app.core import security
from app.core.enums import StudentLevel, TenantType, RoomStatus, LeaseStatus
from app.main import app
from app.db.session import Base
from fastapi.testclient import TestClient
from app.schemas import user as schema_user
from app.services import user_service, lodge_service, tenant_services, room_service, lease_services, payment_service
from app.schemas import tenantprofile as schema_tenant
from app.schemas import lodge as schema_lodge
from app.schemas import room as schema_room
from app.schemas import lease as schema_lease
from app.schemas import payment as schema_payment

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
def tenant_schema_factory():
    """
    A pytest fixture that provides a factory for creating tenant schemas.
    """
    def _create(
            first_name: str = 'Tenant',
            last_name: str = 'A',
            email: str = 'tenant@test.com',
            lodge_id: int = 1,
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
def room_schema_factory():
    """
    A pytest fixture that provides a factory for creating room schemas.
    """
    def _create(
            room_no: str = 'Test Rm-1',
            description: str = 'spacious self con',
            base_rent_price: int = 210000,
            status: RoomStatus = RoomStatus.VACANT,
            lodge_id: int = 1

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
def rooms_in_db(test_db, room_schema_factory, add_landlord_to_db, add_lodge_to_db):
    """
    A pytest fixture that adds multiple rooms to a lodge in the database.
    """
    max_rooms = 50
    db_rooms = []
    for i in range(max_rooms):
        rm_schema = room_schema_factory(
            room_no=f'Test rm{i + 1}',
            description=f'description Test {i + 1}',
            base_rent_price= random.randint(250000, 350000),
            status= RoomStatus.VACANT,
            lodge_id=add_lodge_to_db.id
        )
        new_room = room_service.create_room_for_lodge(
            test_db,
            landlord_id=add_landlord_to_db.id,
            room_in=rm_schema
        )
        db_rooms.append(new_room)
    print(f"\n--- Fixture: rooms_in_ created {len(db_rooms)} tenants. First ID: {db_rooms[0].id}, Last ID: {db_rooms[-1].id} ---")
    return db_rooms

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
    print(f"\n--- Fixture: tenants_in_db created {len(db_tenants)} tenants. First ID: {db_tenants[0].id}, Last ID: {db_tenants[-1].id} ---")
    return db_tenants

@pytest.fixture
def add_tenant_to_db(test_db, mock_tenant_schema, add_lodge_to_db):
    """
    A pytest fixture that adds a tenant to the database.
    """
    t_schema = mock_tenant_schema
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)


@pytest.fixture
def add_room_to_db(test_db, mock_room_schema, add_lodge_to_db):
    """
    A pytest fixture that adds a room to the database.
    """
    return room_service.create_room_for_lodge(test_db, room_in=mock_room_schema, landlord_id=add_lodge_to_db.landlord_id)
    
@pytest.fixture
def add_diff_landlord_room(test_db, room_schema_factory, add_diff_landlord_lodge):
    """
    A pytest fixture that adds a room belonging to a different landlord.
    """
    rm_schema = room_schema_factory(lodge_id=add_diff_landlord_lodge.id)
    return room_service.create_room_for_lodge(test_db, landlord_id=add_diff_landlord_lodge.landlord_id, room_in=rm_schema)

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
    t_schema = tenant_schema_factory(email="tenant2@test.com", first_name="TenantB", lodge_id=add_lodge_to_db.id)
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)

@pytest.fixture
def add_diff_landlord_tenant(test_db, tenant_schema_factory, add_diff_landlord_lodge):
    """
    A pytest fixture that adds a tenant to a different landlord's lodge.
    """
    t_schema = tenant_schema_factory(lodge_id=add_diff_landlord_lodge.id, email="tenant3@test.com")
    return tenant_services.sign_up_tenant(test_db, tenant_in=t_schema)

@pytest.fixture
def lease_schema_factory():
    """
    A pytest fixture that provides a factory for creating LeaseCreate schemas.
    """
    def _create(
        tenant_id: int = 1,
        room_id: int = 1,
        agreed_rent_amt: int = 210000,
        total_amt_paid: int = 105000,
        start_date: date = date.today(),
        end_date: date = date.today() + timedelta(days=365),
        status: LeaseStatus = LeaseStatus.ACTIVE
    ):
        return schema_lease.LeaseCreate(
            tenant_id=tenant_id,
            room_id=room_id,
            agreed_rent_amt=agreed_rent_amt,
            total_amt_paid=total_amt_paid,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
    return _create

@pytest.fixture
def mock_lease_schema(lease_schema_factory):
    """
    A pytest fixture that provides a mock lease schema using the lease_schema_factory.
    """
    return lease_schema_factory()

@pytest.fixture
def add_active_lease_to_db(test_db, lease_schema_factory,add_room_to_db, add_tenant_to_db, add_landlord_to_db):
    """
    Fixture to create and add an active lease to the database directly via the service.
    """
    tenant_id = add_tenant_to_db.id
    room_id = add_room_to_db.id

    lease_schema = lease_schema_factory(status=LeaseStatus.ACTIVE, room_id=room_id, tenant_id=tenant_id)

    return lease_services.create_new_lease(
        db=test_db,
        lease_data=lease_schema,
        landlord_user=add_landlord_to_db
    )

@pytest.fixture
def add_expired_lease_to_db(test_db, lease_schema_factory, add_landlord_to_db, add_tenant_to_db, add_room_to_db):
    """
    Fixture to create and add an expired lease to the database.
    """
    tenant_id = add_tenant_to_db.id
    room_id = add_room_to_db.id
    return lease_services.create_new_lease(
        db=test_db,
        lease_data=lease_schema_factory(status=LeaseStatus.EXPIRED, room_id=room_id, tenant_id=tenant_id),
        landlord_user=add_landlord_to_db
    )

@pytest.fixture
def add_terminated_lease_to_db(test_db, lease_schema_factory, add_landlord_to_db, add_tenant_to_db, add_room_to_db):
    """
    Fixture to create and add a terminated lease to the database.
    """
    tenant_id = add_tenant_to_db.id
    room_id = add_room_to_db.id

    return lease_services.create_new_lease(
        db=test_db,
        lease_data=lease_schema_factory(status=LeaseStatus.TERMINATED, room_id=room_id, tenant_id=tenant_id),
        landlord_user=add_landlord_to_db
    )

@pytest.fixture
def add_pending_termination_lease_to_db(test_db, lease_schema_factory, add_landlord_to_db, add_tenant_to_db,
                                        add_room_to_db):
    """
    Fixture to create and add a lease pending termination to the database.
    """
    tenant_id = add_tenant_to_db.id
    room_id = add_room_to_db.id

    return lease_services.create_new_lease(
        db=test_db,
        lease_data=lease_schema_factory(status=LeaseStatus.PENDING_TERMINATION, tenant_id=tenant_id, room_id=room_id),
        landlord_user=add_landlord_to_db
    )

@pytest.fixture
def add_active_lease_to_diff_landlord_lodge(test_db, lease_schema_factory, add_different_landlord,
                                            add_diff_landlord_tenant, add_diff_landlord_room):
    """
    Fixture to create and add an active lease to a different landlord's lodge.
    """
    lease_data = lease_schema_factory(
        tenant_id=add_diff_landlord_tenant.id,
        room_id=add_diff_landlord_room.id,
        status=LeaseStatus.ACTIVE
    )
    return lease_services.create_new_lease(
        db=test_db,
        lease_data=lease_data,
        landlord_user=add_different_landlord
    )

@pytest.fixture
def leases_in_db(test_db, lease_schema_factory, add_landlord_to_db, tenants_in_db, rooms_in_db):
    """
    A pytest fixture that adds multiple leases to the database.
    It creates a mix of ACTIVE and INACTIVE leases.
    """
    db_leases = []
    # Ensure we have enough rooms and tenants for leases
    num_leases_to_create = min(len(tenants_in_db), len(rooms_in_db), 15) # Limit to 15 or fewer

    for i in range(num_leases_to_create):
        tenant = tenants_in_db[i]
        room = rooms_in_db[i]
        
        # Make every 3rd lease INACTIVE for testing status filters
        status = LeaseStatus.EXPIRED if i % 3 == 0 else LeaseStatus.ACTIVE

        lease_data = lease_schema_factory(
            tenant_id=tenant.id,
            room_id=room.id,
            agreed_rent_amt=room.base_rent_price,
            start_date=date.today() - timedelta(days=random.randint(1, 365)), # Random start date
            end_date=date.today() + timedelta(days=random.randint(1, 365)), # Random end date
            status=status
        )
        new_lease = lease_services.create_new_lease(
            db=test_db,
            lease_data=lease_data,
            landlord_user=add_landlord_to_db
        )
        db_leases.append(new_lease)
    print(
        f"\n--- Fixture: leases_in_db created {len(db_leases)} tenants. First ID: {db_leases[0].id}, Last ID: {db_leases[-1].id} ---")
    return db_leases

@pytest.fixture
def tenant_lease_history_in_db(test_db, lease_schema_factory, add_landlord_to_db, add_tenant_to_db, room_schema_factory, add_lodge_to_db):
    """
    Fixture to create a history of leases for a single tenant.
    Creates 3 EXPIRED leases and 2 ACTIVE leases.
    """
    tenant = add_tenant_to_db
    db_leases = []
    max_history = 5
    # Create 5 rooms for the 5 leases
    for i in range(max_history):
        rm_schema = room_schema_factory(
            room_no=f'History Rm-{i+1}',
            description=f'Room for history test {i+1}',
            base_rent_price= 250000,
            status= RoomStatus.VACANT,
            lodge_id=add_lodge_to_db.id
        )
        new_room = room_service.create_room_for_lodge(test_db, landlord_id=add_landlord_to_db.id, room_in=rm_schema)
        
        # Create 3 EXPIRED and 2 ACTIVE leases
        status = LeaseStatus.EXPIRED if i < 3 else LeaseStatus.ACTIVE
        
        lease_data = lease_schema_factory(
            tenant_id=tenant.id,
            room_id=new_room.id,
            agreed_rent_amt=new_room.base_rent_price,
            start_date=date.today() - timedelta(days=365 * (i+1)) if status == LeaseStatus.EXPIRED else date.today() - timedelta(days=20 * (i + 1)),# Start date in the past
            end_date=date.today() - timedelta(days=365 * i) if status == LeaseStatus.EXPIRED else (date.today() - timedelta(days=20 * (i + 1)))+ timedelta(days=365),
            status=status
        )
        
        new_lease = lease_services.create_new_lease(
            db=test_db,
            lease_data=lease_data,
            landlord_user=add_landlord_to_db
        )
        db_leases.append(new_lease)
        
    return tenant, db_leases

@pytest.fixture
def payment_schema_factory():
    """
    A pytest fixture that provides a factory for creating PaymentCreate schemas.
    """
    def _create(
        amount_paid: int = 50000,
        lease_id: int = 1
    ):
        return schema_payment.PaymentCreate(
            amount_paid=amount_paid,
            lease_id=lease_id
        )
    return _create

@pytest.fixture
def mock_payment_schema(payment_schema_factory):
    """
    A pytest fixture that provides a mock payment schema using the payment_schema_factory.
    """
    return payment_schema_factory()

@pytest.fixture
def add_payment_to_db(test_db, payment_schema_factory, add_active_lease_to_db, add_landlord_to_db):
    """
    Fixture to create and add a payment to the database.
    """
    p_schema = payment_schema_factory(
        lease_id=add_active_lease_to_db.id
    )
    return payment_service.add_payment_record(
        db=test_db,
        current_landlord_id=add_landlord_to_db.id,
        payment_data=p_schema
    )

@pytest.fixture
def multiple_safe_payments_in_db(test_db, payment_schema_factory, add_landlord_to_db, add_active_lease_to_db):
    """
    Fixture to create multiple payments for a tenant's lease that stay within the agreed rent amount.
    Calculates remaining balance after lease creation and distributes it evenly across payments.
    Returns (list of all payments on the lease, the lease object).
    """
    from app.crud.payment import crud_payment

    lease = add_active_lease_to_db
    num_payments = 5

    # Find out how much has already been paid (from lease creation's initial payment)
    already_paid = crud_payment.get_payments_aggregate_by_lease_id(test_db, lease_id=lease.id)
    remaining_balance = lease.agreed_rent_amt - already_paid

    # Divide the remaining balance evenly, ensuring we don't exceed it
    amount_per_payment = remaining_balance // num_payments

    for i in range(num_payments):
        payment_data = payment_schema_factory(
            amount_paid=amount_per_payment,
            lease_id=lease.id
        )
        payment_service.add_payment_record(
            db=test_db,
            current_landlord_id=add_landlord_to_db.id,
            payment_data=payment_data
        )

    all_payments = payment_service.fetch_payments_by_lease(
        db=test_db,
        lease_id=lease.id,
        landlord_id=add_landlord_to_db.id
    )
    return all_payments, lease

@pytest.fixture
def tenant_safe_payments_in_db(test_db, payment_schema_factory, add_landlord_to_db, add_active_lease_to_db):
    """
    Fixture to create multiple safe payments for a specific tenant's lease.
    Designed for tenant-side payment fetch tests (e.g. /payments/me/{lease_id}).
    Calculates remaining balance and distributes it across payments without exceeding agreed rent.
    Returns (list of all payments on the lease, the lease object).
    """
    from app.crud.payment import crud_payment

    lease = add_active_lease_to_db
    num_payments = 5

    already_paid = crud_payment.get_payments_aggregate_by_lease_id(test_db, lease_id=lease.id)
    remaining_balance = lease.agreed_rent_amt - already_paid
    amount_per_payment = remaining_balance // num_payments

    for i in range(num_payments):
        payment_data = payment_schema_factory(
            amount_paid=amount_per_payment,
            lease_id=lease.id
        )
        payment_service.add_payment_record(
            db=test_db,
            current_landlord_id=add_landlord_to_db.id,
            payment_data=payment_data
        )

    # Fetch payments through the tenant path to mirror how tenant tests will consume them
    tenant_payments = payment_service.fetch_tenant_lease_payments(
        db=test_db,
        lease_id=lease.id,
        tenant_id=lease.tenant_id,
        skip=None,
        limit=None
    )
    return tenant_payments, lease