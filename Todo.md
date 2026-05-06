# 📋 Active Task Tracker

## Epic 1: Phase 1 - Identity & Access Management (Landlord Auth)
**Concept Focus:** Authentication, Password Hashing, JWT Statelessness.

### ✅ Completed Tasks
- [x] Review and approve the initial PM System Status Report.
- [x] Ensure project directory, virtual environment, and initial `requirements.txt` are clean and ready.
- [x] **Task 1.1:** Define `User` SQLAlchemy model (Table: `users`).
  - **Fields:** `id` (PK), `email` (Unique, Index), `hashed_password`, `is_active`, `created_at`.
- [x] **Task 1.3:** Create Pydantic schemas for User (`UserCreate`, `UserResponse`), with `password` `max_length` increased to 128.
- [x] **Task 1.4:** Implement secure password hashing utility functions using `passlib`.
- [x] **Task 1.4.1:** Install `passlib[bcrypt]` and `python-multipart` (if not already in `requirements.txt`).
- [x] **Task 1.4.2:** Create `app/core/security.py` file.
- [x] **Task 1.4.3:** Implement `get_password_hash(password: str) -> str` using `bcrypt` in `app/core/security.py`.
- [x] **Task 1.4.4:** Implement `verify_password(plain_password: str, hashed_password: str) -> bool` using `bcrypt` in `app/core/security.py`.
- [x] **Task 1.5:** Build the `create_landlord` CRUD operation.
- [x] **Task 1.5.1:** Create `app/crud/user.py` file.
- [x] **Task 1.5.2:** Implement `create_user(db: Session, user: UserCreate) -> User` in `app/crud/user.py`. 
- [x] **Task 1.5.3:** Implement `get_user_by_email(db: Session, email: str) -> User | None` in `app/crud/user.py`.
- [x] **Task 1.6:** Build the `POST /auth/register` API Router.
- [x] **Task 1.6.1:** Create `app/api/v1/auth.py` file.
- [x] **Task 1.6.2:** Define a FastAPI `APIRouter` for authentication endpoints.
- [x] **Task 1.6.3:** Implement the `POST /auth/register` endpoint.
- [x] **Task 1.7:** Build the `POST /auth/token` (login) API Router.
- [x] **Task 1.7.1:** Implement `authenticate_user(db: Session, email: str, password: str) -> User | None` in `app/crud/user.py`.
- [x] **Task 1.7.2:** Implement `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str` in `app/core/security.py`.
- [x] **Task 1.7.3:** Implement the `POST /auth/token` endpoint.
- [x] **Task 1.8:** Implement `get_current_user` and `get_current_active_user` dependencies.
- [x] **Task 1.8.1:** Implement `get_current_user(token: str = Depends(oauth2_scheme)) -> User` in `app/api/deps.py`. 
- [x] **Task 1.8.2:** Implement `get_current_active_user`.

## Epic 2: Phase 2 - Core Domain Entities (Lodge & Rooms)
**Concept Focus:** SQLAlchemy Foreign Keys, UniqueConstraints, Pydantic Nested Schemas, Hierarchical Routing, Exception Bubbling.

### 📝 Pending Tasks
- [ ] **Task 2.6:** Refactor Room creation to properly resolve relationships (e.g. Lodge validation before Room creation).
- [ ] **Task 2.7:** Ensure robust exception bubbling from CRUD layer through Service Layer up to Routers.

### ✅ Completed Tasks
- [x] **Task 2.1:** Create `Lodge` SQLAlchemy Model (`app/models/lodge.py`).
- [x] **Task 2.2:** Create `Room` Pydantic Schemas (`app/schemas/room.py`).
- [x] **Task 2.3:** Refactor `Room` CRUD operations (`app/crud/room.py`) to use exact matches for room numbers, not wildcards.
- [x] **Task 2.4:** Build `Room` Service Orchestrator (`app/services/room_service.py`).
- [x] **Task 2.5:** Refactor `Room` API Router (`app/api/v1/rooms.py`) to use hierarchical routing.

## Epic 3: User Service Refactoring
**Concept Focus:** Service Layer Orchestration, Polymorphic Input Handling, Schema Composition, Database Transactions.

### 📝 Pending Tasks
- [ ] **Task 3.6:** Review security implementation for Tenant endpoints (Ensure Tenants can only edit their own profile, Landlords can access Lodge tenants).

### ✅ Completed Tasks
- [x] Review `sign_up_user` in `app/services/user_service.py`.
- [x] **Task 3.1:** Refactor Pydantic Schemas to remove redundant fields in responses. 
- [x] **Task 3.2:** Fix `TenantProfileCreate` schema.
- [x] **Task 3.3:** Finalize `TenantProfileResponse` schema to remove all redundant data and security leaks.
- [x] **Task 3.4:** Refactor `register_tenant` in `app/services/user_service.py` to fix transaction rollback bug and unpacking logic using `db.flush()`.
- [x] **Task 3.4.1:** Delete redundant `create_tenant` from `app/crud/tenantprofile.py`.
- [x] **Task 3.5:** Build `Tenant` API Router (`app/api/v1/tenants.py`).

## Epic 4: Payment and Lease Infrastructure
**Concept Focus:** Business logic, Date management, Complex object updates.

### 📝 Pending Tasks
- [ ] **Task 4.1:** Build `Lease` Service orchestrator. 
- [ ] **Task 4.2:** Build `Payment` Service orchestrator.

---
*Note: The PM (AI) will automatically append to this file upon task completion. Do not delete historical items.*