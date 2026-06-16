# LodgeManager API

**A Modern Property & Lodge Management System** built with **FastAPI**.

This is a robust backend designed for efficient management of student accommodations and rental properties. It handles everything from tenant onboarding and room assignments to complex financial aggregations and dashboard reporting.

---

## 🚀 Features

### Core Business Modules
- **Authentication & Authorization:** Secure JWT-based authentication with role-based access control (Landlord & Tenant).
- **Lodge & Room Management:** Manage properties, room status (Safe, Expiring, Overdue, Owing, Vacant, Maintenance), and track occupancy.
- **Tenant Management:** Track tenant profiles, user details, and active statuses.
- **Lease & Contract Management:** Handle lease agreements and terms seamlessly.
- **Payment & Financial Tracking:** Record rent payments, calculate outstanding debts, and aggregate financial metrics (expected vs. collected revenue).

### Advanced Dashboard & Analytics
- **Landlord Dashboard:** Provides a real-time overview of the lodge.
- **Financial Aggregations:** Complex SQLAlchemy queries to accurately compute potential income, unpaid rent, and active lease financials dynamically.
- **Entity Count Summaries:** Aggregated counts for total rooms, occupied rooms, maintenance rooms, and total tenants based on customizable filters.

### Technical Highlights
- **Clean Architecture:** Strict separation between Presentation (Routers), Business Logic (Services), Data Access (CRUD), and Domain Models.
- **High-Performance ORM:** Utilizing **SQLAlchemy 2.0** with raw SQL queries, subqueries, and advanced aggregations (`func.sum`, `outerjoin`) for performance.
- **Data Validation:** Strict schema definitions using **Pydantic v2**.
- **Comprehensive Testing:** A robust suite of automated tests using `pytest` to guarantee application reliability.
- **Migrations:** Managed database schema versioning with **Alembic**.

---

## 🛠 Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| **Backend**    | Python 3.11+, FastAPI               |
| **ORM**        | SQLAlchemy 2.0 + Alembic            |
| **Validation** | Pydantic v2                         |
| **Auth**       | JWT, Passlib + Bcrypt               |
| **Testing**    | Pytest                              |

---

## 📁 Project Structure

```bash
.
├── alembic/                  # Database migration scripts and versions
├── app/                      # Main Backend Application source code
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── todos.py              # Epic-level task tracking
│   ├── api/                  # API routing layer
│   │   ├── __init__.py
│   │   ├── deps.py           # Dependency injection (e.g., auth checks)
│   │   └── v1/               # API version 1 endpoints
│   │       ├── __init__.py
│   │       ├── leases.py     # Lease management endpoints
│   │       ├── lodges.py     # Lodge management endpoints
│   │       ├── payments.py   # Payment tracking endpoints
│   │       ├── rooms.py      # Room management endpoints
│   │       ├── tenants.py    # Tenant profile endpoints
│   │       ├── user.py       # User authentication endpoints
│   │       └── dashboards/   # Dashboard aggregation endpoints
│   │           ├── landlord_dashboard.py # Landlord stats overview
│   │           └── tenant_dashboard.py   # Tenant stats overview
│   ├── core/                 # Application configuration and settings
│   │   ├── __init__.py
│   │   ├── config.py         # Environment variables and settings
│   │   ├── constants.py      # Global constants
│   │   ├── enums.py          # Enum definitions (e.g., RoomStatus)
│   │   ├── exceptions.py     # Custom domain exceptions
│   │   ├── handlers.py       # Global exception handlers
│   │   └── security.py       # Password hashing and token generation
│   ├── crud/                 # Data Access Layer (CRUD operations)
│   │   ├── __init__.py
│   │   ├── base_crud.py      # Generic CRUD functionality
│   │   ├── lease.py          # Lease database operations
│   │   ├── lodge.py          # Lodge database operations
│   │   ├── payment.py        # Payment database operations
│   │   ├── room.py           # Room database operations
│   │   ├── tenantprofile.py  # Tenant database operations
│   │   └── user.py           # User database operations
│   ├── db/                   # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py           # SQLAlchemy declarative base
│   │   └── session.py        # Database session management
│   ├── models/               # SQLAlchemy ORM definitions
│   │   ├── __init__.py
│   │   ├── lease.py          # Lease SQL table model
│   │   ├── lodge.py          # Lodge SQL table model
│   │   ├── payment.py        # Payment SQL table model
│   │   ├── room.py           # Room SQL table model
│   │   ├── tenantprofile.py  # Tenant Profile SQL table model
│   │   └── user.py           # User SQL table model
│   ├── schemas/              # Pydantic validation models
│   │   ├── __init__.py
│   │   ├── dashboard.py      # Dashboard response schemas
│   │   ├── entity_count.py   # Entity count summary schemas
│   │   ├── financial.py      # Financial summary schemas
│   │   ├── generic_extras.py # Shared schema components
│   │   ├── lease.py          # Lease DTOs
│   │   ├── lodge.py          # Lodge DTOs
│   │   ├── payment.py        # Payment DTOs
│   │   ├── room.py           # Room DTOs
│   │   ├── tenantprofile.py  # Tenant DTOs
│   │   └── user.py           # User DTOs
│   └── services/             # Business Logic Layer
│       ├── __init__.py
│       ├── dashboard_service.py # Dashboard data aggregation
│       ├── lease_services.py    # Lease creation rules
│       ├── lodge_service.py     # Lodge management rules
│       ├── payment_service.py   # Payment calculation rules
│       ├── room_service.py      # Room status rules
│       ├── tenant_services.py   # Tenant onboarding rules
│       └── user_service.py      # User authentication rules
├── test/                     # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures and test DB setup
│   ├── test_auth.py          # Auth endpoint tests
│   ├── test_example.py       # Boilerplate test examples
│   ├── test_lease.py         # Lease logic tests
│   ├── test_lodge.py         # Lodge logic tests
│   ├── test_main.py          # App startup tests
│   ├── test_payment.py       # Payment calculation tests
│   ├── test_room.py          # Room logic tests
│   └── test_tenant.py        # Tenant logic tests
├── utilities/                # Helper scripts
│   └── dashboard_utilities.py # Dashboard filtering helpers
├── .gitignore                # Git ignored files list
├── alembic.ini               # Alembic configuration
├── Project_Architecture_Report.md # Detailed architecture design document
├── pytest.ini                # Pytest configuration
├── README.md                 # Primary project documentation
├── requirements.txt          # Python pip dependencies
└── test_main.http            # HTTP requests for manual testing
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/DonaldXoftDev/LodgeManagerAPIProject.git
cd LodgeManagerAPIProject

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env

# 5. Run database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload
```

### Accessing the API:
Once running, you can interact with the API documentation at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests
The project contains a thorough test suite. To run the tests, execute:
```bash
pytest
```

---

## 🤝 Contributing
Feedback, suggestions, and contributions are very welcome! Feel free to open issues or submit pull requests.
