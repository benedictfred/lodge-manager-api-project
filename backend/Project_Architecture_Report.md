# Lodge Management System - System Architecture Report

## 1. Executive Summary & Tech Stack

The Lodge Management System is a modern, API-first backend designed to facilitate property management for landlords. Its primary function is to track physical assets (Lodges and Rooms), manage occupancy (Tenants and Leases), and handle financial oversight (Rent Payments). The architecture has evolved from a simple monolithic CRUD application into a robust, domain-driven service architecture, prepared for multi-tenancy and complex business logic.

**Core Tech Stack:**
*   **Framework:** FastAPI (Python 3.10+) - Chosen for its high performance, asynchronous support, and automatic OpenAPI documentation.
*   **Database ORM:** SQLAlchemy 2.0 - Utilized for defining data models, enforcing constraints, and managing complex table relationships.
*   **Data Validation:** Pydantic V2 - Ensures strict type-checking and serialization/deserialization of API payloads.
*   **Authentication:** OAuth2 with JWT (JSON Web Tokens) - Provides stateless, scalable, and secure session management via `passlib` (bcrypt).
*   **Database Engine:** SQLite (configured for local MVP development, heavily abstracted for easy migration to PostgreSQL).
*   **Migrations:** Alembic - Tracks schema changes over time.

## 2. Architectural Pattern & File Structure

The project strictly adheres to a **Layered Architecture**, heavily influenced by Domain-Driven Design (DDD) principles. Specifically, it employs the **Service-Repository Pattern**. This pattern ensures that the API routers (Presentation), the business rules (Service), and the database queries (Repository/CRUD) remain highly decoupled.

**Directory Mapping (`app/`):**
*   `api/v1/`: **Presentation Layer**. Contains the FastAPI routers. These are "thin" controllers.
*   `services/`: **Business Logic Layer**. Contains the "Orchestrators". This is where validation, multi-table transactions, and domain rules live.
*   `crud/`: **Data Access Layer (Repository)**. Contains the "Workers". Strictly limited to direct SQLAlchemy database operations.
*   `models/`: **Domain Entities**. The physical representation of data structures in the SQL database.
*   `schemas/`: **Data Transfer Objects (DTOs)**. Pydantic models defining the exact shape of JSON entering and leaving the API.
*   `core/`: Application-wide settings, security protocols, and global custom exceptions.
*   `db/`: Database connection pooling and session management.

## 3. Component Layers Breakdown

### Presentation Layer (`app/api/v1/`)
*   **Responsibility:** To accept incoming HTTP requests, enforce authentication via Dependency Injection (`Depends(get_landlord_user)`), hand off the payload to the Service Layer, and translate any resulting data or custom exceptions into standardized HTTP responses (e.g., 200 OK, 404 Not Found, 400 Bad Request).
*   **Design Choice:** **Hierarchical Routing**. Routes are structured to reflect resource ownership (e.g., `GET /lodges/{lodge_id}/rooms` rather than a global `GET /rooms`). This prevents route collisions and enforces logical boundaries.

### Business Logic Layer (`app/services/`)
*   **Responsibility:** Acts as the "Head Chef". It orchestrates multiple CRUD calls to fulfill a single business request.
*   **Key Implementations:**
    *   **Authorization:** Explicit checks verify ownership before action (e.g., `lodge_service.verify_lodge_ownership`).
    *   **Atomic Transactions:** Operations that affect multiple tables (like registering a tenant, which creates a `User` and a `TenantProfile`) use manual transaction management (`db.flush()` and `db.rollback()`) to prevent orphaned records.
    *   **Exception Bubbling:** When business rules fail (e.g., "Room is already occupied"), services raise explicit custom Python exceptions (`ActiveLeaseFoundError`) rather than returning `None`.

### Data Access Layer (`app/crud/`)
*   **Responsibility:** Execution of raw database queries.
*   **Key Implementations:**
    *   **`CRUDBase`:** A generic class providing standard `get`, `create`, and `update` functionality, enforcing the DRY principle.
    *   **Explicit Overrides:** When complex filtering is required (e.g., `get_active_room_and_tenant_lease`), specific methods are written in the domain's CRUD file. The project favors explicit DB queries over loading massive relationships into memory for filtering.

### Data Transfer Objects (`app/schemas/`)
*   **Responsibility:** Defining the input/output contract of the API.
*   **Key Implementations:**
    *   **Composition over Inheritance:** Schemas like `TenantProfileResponse` correctly nest `UserResponse` objects rather than inheriting all their fields, preventing data redundancy.
    *   **Security:** Output schemas explicitly exclude sensitive fields like `hashed_password`.

## 4. Core Data Flow (Example: Creating a Lease)

1.  **Client Request:** Frontend sends a `POST /api/v1/leases/` request with a JSON payload containing `room_id`, `tenant_id`, and `agreed_rent_amt`.
2.  **Presentation (Router):** `app/api/v1/leases.py` receives the request. FastAPI validates the JSON against `schema_lease.LeaseCreate`. It also injects the `landlord_user` via the authentication dependency.
3.  **Service (Orchestrator):** The router calls `lease_services.create_new_lease(...)`.
4.  **Validation (Service -> CRUD):** The service queries `crud_room` and `crud_tenant` to ensure both entities exist. It then checks if `room.lodge.landlord_id` matches the current user. Finally, it queries `crud_lease` to ensure the room is not already occupied (`ActiveLeaseFoundError`).
5.  **Execution (CRUD):** If all rules pass, the service calls `crud_lease.create_lease()`.
6.  **Database Commit:** The CRUD layer instantiates the SQLAlchemy model, updates the Room status to OCCUPIED, and calls `db.commit()`.
7.  **Response:** The newly created Lease object bubbles back up to the router, where FastAPI uses `schema_lease.LeaseResponse` to serialize it into JSON for the client.

## 5. Security & Error Handling Posture

*   **Authentication:** Stateless. A successful login (`POST /api/v1/auth/login`) returns a JWT. Subsequent requests must include this token in the `Authorization: Bearer` header.
*   **Role-Based Access Control (RBAC):** Implemented cleanly via Dependency Injection. Endpoints are protected by specific functions like `get_landlord_user` or `get_tenant_user` (in `app/api/deps.py`), which decode the JWT and check the `User.role` attribute before allowing route execution.
*   **Error Handling:** The project successfully avoids "Leaky Abstractions". The CRUD layer returns models or `None`. The Service layer interprets `None` as a business failure and raises a Custom Exception (defined in `app/core/exceptions.py`). The API Router uses `try...except` blocks to catch these specific exceptions and throw user-friendly `HTTPException` responses.

## 6. Technical Debt & Architect's Recommendations

Based on the current audit, the project has a strong foundation, but requires immediate attention in a few key areas to ensure scalability and data integrity:

*   **Recommendation 1: Fix Transaction Management in Lease Creation.**
    *   *Issue:* In `app/crud/lease.py` (assuming the commented code is the implementation), `create_lease` alters both the `Lease` table and the `Room` table's status. If an error occurs between the `db.add(db_lease)` and `db.commit()`, it could lead to inconsistent states.
    *   *Action:* Refactor this to use the same atomic transaction pattern implemented in `user_service.py`. The *Service Layer* should manage the state change of the room and the creation of the lease, using `try...except` and `db.rollback()` to ensure both succeed or both fail.

*   **Recommendation 2: Standardize the `update_room_details` Service.**
    *   *Issue:* In `app/services/room_service.py`, `update_room_details` successfully fetches the room but currently returns early (`return lodge`), leaving the actual `crud_room.update()` call as unreachable dead code. Furthermore, it lacks the explicit ownership verification check (`room.lodge.landlord_id != landlord_id`) before updating.
    *   *Action:* Remove the early return. Implement the ownership check. Ensure the `update_data` payload is properly passed to the CRUD layer.

*   **Recommendation 3: Consolidate Route Design in Leases & Tenants.**
    *   *Issue:* The route `POST /api/v1/leases/` does not include the `lodge_id` in the URL hierarchy, while `GET /api/v1/leases/{lodge_id}` does. This inconsistency makes the API harder to consume.
    *   *Action:* Standardize route paths. If a lease strictly belongs to a room, and a room belongs to a lodge, consider `POST /api/v1/lodges/{lodge_id}/leases` to ensure the context is always present and the landlord's ownership of the building can be verified immediately at the router/service boundary.

## 7. Active Task Tracker (Next Steps)
*(The PM AI is configured to maintain a detailed Todo.md file, which tracks Epic-level tasks. Note: Some task tracking files have been moved to `.gitignore` to prevent cluttering the repository).*

**Current Priorities:**
1.  **Task 5.1:** Fix unreachable code in `app/services/room_service.py` (`update_room_details`).
2.  **Task 5.2:** Refactor `app/api/v1/leases.py` to use `{lodge_id}` hierarchy for `POST` routes.
3.  **Task 5.3:** Refactor `crud_lease.py` or `lease_services.py` to handle lease creation and room status updates via a single atomic `db.commit()`.
