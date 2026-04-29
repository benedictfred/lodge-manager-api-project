# 🏗️ Lodge Manager API - Architectural Roadmap

## 1. Core Philosophy
* **Outside-In Design:** Frontend UI mockups dictate backend JSON payloads. If the UI doesn't need it, the backend doesn't serve it.
* **Separation of Concerns:** Routers handle HTTP/Web logic. CRUD files handle DB execution. Models dictate structure. Schemas dictate data validation.
* **Zero Trust Security:** All endpoints (except public ones like Register/Login) require JWT authentication. Landlords can ONLY access entities tied to their `landlord_id`.

## 2. Entity Relationship Diagram (ERD) Blueprint
* **Landlord (User)** 
  * Independent Entity. 
  * Holds credentials (email, hashed_password).
* **Lodge (Property)**
  * Depends on: `Landlord` (Many-to-One).
  * Contains: Name, Address.
* **Room (Unit)**
  * Depends on: `Lodge` (Many-to-One).
  * Contains: Room Number, Price, Status.
* **Tenant (Occupant)**
  * Depends on: `Room` (One-to-One / Many-to-One based on future scope).
  * Contains: Name, Email, Phone.

## 3. Engineering Concepts Tracker
*As we build, we master these language-agnostic concepts:*
- [ ] **Authentication vs. Authorization:** (Identity vs. Permissions).
- [ ] **Statelessness (JWTs):** Why servers shouldn't remember who you are between requests.
- [ ] **Data Integrity (Foreign Keys & Cascades):** Preventing orphaned data.
- [ ] **Idempotency:** Making safe retries (e.g., using PUT instead of POST).
- [ ] **Pagination:** Handling large data sets without crashing the server.

## 4. Phase Rollout
* **Phase 1:** Identity & Access Management (IAM) - Landlord Auth.
* **Phase 2:** Portfolio Foundation - Lodge Management.
* **Phase 3:** Unit Tracking - Room Management.
* **Phase 4:** Occupant Assignment - Tenant Management.
* **Phase 5:** Financials - Rent & Lease Tracking.