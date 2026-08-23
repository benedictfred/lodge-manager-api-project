# 📖 LodgeOps: Master User Stories & Code Execution Verification

This document defines the complete functional specification, user personas, end-to-end multi-step workflow combinations, and **forensic layer-by-layer code execution audit (Endpoint ➔ Service ➔ CRUD ➔ Model)** for all active endpoints in the **LodgeOps** API (`v1`).

---

## 👥 Personas & Roles

* **👨‍💼 Landlord (`UserRole.LANDLORD`):** The property owner responsible for setting up lodges, configuring rooms, reviewing tenant applications, creating leases, recording payments, and monitoring portfolio financials.
* **🎓 Tenant (`UserRole.TENANT`):** A university student residing in or applying to a lodge. Responsible for completing their student profile, tracking lease duration, viewing payment history, and requesting termination.
* **🔒 System / Public User (Unauthenticated):** A prospective student resolving an invitation link before account creation.

---

# 🔬 FORENSIC LAYER-BY-LAYER CODE AUDIT (Endpoint ➔ Service ➔ CRUD ➔ Model)

| # | Endpoint Route & Method | Service Layer Function (`app/services/*`) | CRUD Layer Function (`app/crud/*`) | Core Database Models Touched (`app/models/*`) | Key Invariants Enforced in Code |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | `POST /api/v1/users/register/landlord` | `user_service.sign_up_landlord` | `crud_user.get_user_by_email`<br>`crud_user.create` | `User` | Duplicate email check; bcrypt hashing; forces `UserRole.LANDLORD`. |
| **2** | `POST /api/v1/users/register/tenant` | `tenant_services.sign_up_tenant` | `crud_invite.get_invite_record_by_id`<br>`crud_user.get_user_by_email`<br>`crud_tenant.create_tenant` | `User`<br>`TenantProfile`<br>`Invite` | Checks `invite.is_expired`; checks `invite.status != ACCEPTED`; creates `TenantProfile(status=PENDING)`; marks `Invite(status=ACCEPTED)`. |
| **3** | `POST /api/v1/users/login` | `user_service.login_authenticated_user` | `crud_user.get_user_by_email`<br>`crud_user.create_new_refresh_token_record` | `User`<br>`RefreshToken` | `verify_password_hash`; issues JWT access token; sets HttpOnly session cookies. |
| **4** | `POST /api/v1/users/refresh` | `user_service.refresh_access_token` | `crud_user.get`<br>`crud_user.get_refresh_token`<br>`crud_user.delete_refresh_token`<br>`crud_user.create_new_refresh_token_record` | `User`<br>`RefreshToken` | JWT signature verification; validates active user; single-use token rotation (deletes old token, writes new one). |
| **5** | `GET /api/v1/users/me` | *Dependency Injection* (`get_current_user`) | `crud_user.get` | `User` | Validates JWT bearer/cookie; returns authenticated identity. |
| **6** | `POST /api/v1/users/logout` | `user_service.logout_authenticated_user` | `crud_user.delete_refresh_token` | `RefreshToken` | Deletes DB session token; clears HttpOnly response cookies. |
| **7** | `POST /api/v1/invites/` | `invite_service.invite_tenant` | `lodge_service.verify_lodge_ownership`<br>`crud_invite.add_invite_record` | `Invite`<br>`Lodge` | Verifies landlord owns lodge; generates UUIDv7 token with expiration timestamp. |
| **8** | `GET /api/v1/invites/{invite_id}` | `invite_service.fetch_invite_record` | `crud_invite.get_invite_record_by_id` | `Invite`<br>`Lodge` | Public access; evaluates dynamic `@property is_expired`; returns lodge name. |
| **9** | `POST /api/v1/lodges/register` | `lodge_service.create_new_lodge_for_landlord` | `crud_lodge.get_by_name_and_landlord`<br>`crud_lodge.insert_lodge_tree` | `Lodge`<br>`Room` | Unique lodge name per landlord; supports optional `room_generator` for bulk room pre-creation. |
| **10** | `GET /api/v1/lodges/` | `crud_lodge.get_lodges_by_owner` | `crud_lodge.get_lodges_by_owner` | `Lodge` | Landlord-scoped list query with pagination (`skip`, `limit`). |
| **11** | `GET /api/v1/lodges/{lodge_id}` | `lodge_service.verify_lodge_ownership` | `crud_lodge.get` | `Lodge` | Strict ownership verification: raises `LodgeNotFoundError` if owned by another landlord. |
| **12** | `PATCH /api/v1/lodges/{lodge_id}` | `lodge_service.update_landlord_lodge` | `lodge_service.verify_lodge_ownership`<br>`crud_lodge.update` | `Lodge` | Ownership check; updates lodge name, address, or description. |
| **13** | `GET /api/v1/lodges/{lodge_id}/tenants` | `tenant_services.fetch_lodge_tenants` | `lodge_service.verify_lodge_ownership`<br>`crud_tenant.get_tenants` | `TenantProfile`<br>`Lodge` | Ownership check; filters tenants by lodge and optional status (`PENDING`, `APPROVED`, `REJECTED`). |
| **14** | `POST /api/v1/rooms/` | `room_service.create_room_for_lodge` | `lodge_service.verify_lodge_ownership`<br>`crud_room.get_room_by_lodge_and_number`<br>`crud_room.create` | `Room`<br>`Lodge` | Verifies lodge ownership; checks room number uniqueness within the lodge; initializes room. |
| **15** | `GET /api/v1/rooms/{lodge_id}/rooms` | `room_service.get_lodge_rooms` | `lodge_service.verify_lodge_ownership`<br>`crud_room.get_rooms` | `Room`<br>`Lodge` | Paginated room inventory query for a specific lodge. |
| **16** | `GET /api/v1/rooms/{room_id}` | `room_service.get_room_details` | `room_service.verify_room_existence`<br>`crud_room.get` (joinedload `Room.lodge`) | `Room`<br>`Lodge` | Ownership check across joined relations; returns deep room data. |
| **17** | `PATCH /api/v1/rooms/{room_id}` | `room_service.update_room_details` | `room_service.verify_room_existence`<br>`crud_room.update` | `Room` | **Occupancy Guard:** raises `RoomIsOccupiedError` if room has active lease; validates status against allowed updatable constants. |
| **18** | `PATCH /api/v1/rooms/{lodge_id}/rooms/bulk` | `room_service.bulk_update_base_rent` | `lodge_service.verify_lodge_ownership`<br>`crud_room.get_updatable_rooms` | `Room` | Verifies lodge ownership; ensures all target rooms exist; raises `RoomIsOccupiedError` if any room is occupied; updates base rent atomically. |
| **19** | `GET /api/v1/tenants/profile` | `tenant_services.fetch_tenant` | `current_user.tenant_profile` | `TenantProfile`<br>`User` | Resolves authenticated tenant's profile. |
| **20** | `PATCH /api/v1/tenants/profiles/me` | `tenant_services.update_tenant_profile` | `crud_tenant.update_tenant` | `TenantProfile`<br>`User` | Updates student level, department, reg no, emergency phone. |
| **21** | `GET /api/v1/tenants/profile/{tenant_id}` | `tenant_services.fetch_tenant_by_landlord` | `crud_tenant.get` (joinedload `TenantProfile.lodge`) | `TenantProfile`<br>`Lodge` | Cross-checks `tenant.lodge.landlord_id == current_user.id`; returns full student record. |
| **22** | `PATCH /api/v1/tenants/{tenant_id}` | `tenant_services.update_tenant_profile_status` | `crud_tenant.get` (joinedload `TenantProfile.lodge`)<br>`crud_tenant.update` | `TenantProfile` | Ownership check; **blocks resetting to `PENDING`**; sets status to `APPROVED` or `REJECTED`. |
| **23** | `DELETE /api/v1/tenants/{tenant_id}` | `crud_tenant.delete_tenant` | `crud_tenant.delete_tenant` | `TenantProfile` | Purges tenant profile record from database. |
| **24** | `POST /api/v1/leases/` | `lease_services.create_new_lease` | `room_service.verify_room_existence`<br>`crud_tenant.get`<br>`crud_lease.get_active_lease_for_room`<br>`payment_service.can_add_payment`<br>`crud_lease.create_lease` | `Lease`<br>`Room`<br>`TenantProfile`<br>`Payment` | **5 Core Invariants:**<br>1. Room belongs to landlord.<br>2. Tenant belongs to same lodge.<br>3. Room has no active lease.<br>4. Upfront payment `<= agreed_rent`.<br>5. Tenant status `== APPROVED`. |
| **25** | `GET /api/v1/leases/{lodge_id}` | `lease_services.get_filtered_landlord_leases` | `lodge_service.verify_lodge_ownership`<br>`crud_lease.get_tenant_leases` | `Lease` | Landlord lease browser with multi-dimensional filtering (by room, tenant ID, or status). |
| **26** | `GET /api/v1/leases/tenant/me` | `lease_services.get_filtered_leases_tenant` | `crud_lease.get_tenant_leases` | `Lease`<br>`TenantProfile` | Tenant self-contract history lookup. |
| **27** | `PATCH /api/v1/leases/{lease_id}` | `lease_services.update_lease_details` | `crud_lease.get` (joinedload `Room.lodge`)<br>`crud_lease.update` | `Lease` | Verifies landlord ownership via `room.lodge`; amends lease terms. |
| **28** | `PATCH /api/v1/leases/terminate/{lease_id}` | `lease_services.terminate_lease` | `lease_services.verify_lease_to_terminate`<br>`crud_lease.lease_terminate` | `Lease`<br>`Room` | Validates lease is not already terminated; sets `Lease.status=TERMINATED`; sets `Lease.actual_end_date=today`; sets `Room.status=VACANT`. |
| **29** | `PATCH /api/v1/leases/me/terminate/{lease_id}` | `lease_services.appeal_for_lease_termination` | `lease_services.verify_lease_to_terminate`<br>`lease_services.verify_tenant_owns_lease`<br>`crud_lease.request_terminate_lease` | `Lease` | Validates tenant ownership; validates lease is active; sets `Lease.status=PENDING_TERMINATION`. |
| **30** | `POST /api/v1/payments/create-payment` | `payment_service.add_payment_record` | `crud_lease.get` (joinedload `Room.lodge`)<br>`crud_payment.get_payments_aggregate_by_lease_id`<br>`payment_service.can_add_payment`<br>`crud_payment.create` | `Payment`<br>`Lease`<br>`Room` | **Ledger Ceiling Guard:** Verifies landlord ownership; blocks payments on terminated leases; prevents overpayments (`total + incoming <= agreed_rent`). |
| **31** | `GET /api/v1/payments/{lease_id}` | `payment_service.fetch_payments_by_lease` | `crud_lease.get` (joinedload `Room.lodge`)<br>`crud_payment.get_lease_payments` | `Payment`<br>`Lease` | Landlord audit trail of all installment transactions for a specific lease. |
| **32** | `GET /api/v1/payments/me/{lease_id}` | `payment_service.fetch_tenant_lease_payments` | `crud_lease.get`<br>`lease_services.verify_tenant_owns_lease`<br>`crud_payment.get_lease_payments` | `Payment`<br>`Lease` | Tenant itemized receipt lookup for their own lease payments. |
| **33** | `GET /api/v1/dashboard-landlord/me/landlord/{lodge_id}` | `dashboard_service.get_landlord_dashboard` | `lodge_service.verify_lodge_ownership`<br>`crud_payment.get_potential_income_from_rooms`<br>`crud_payment.get_financials_for_active_leases`<br>`crud_payment.get_financial_for_forecasted_empty_rooms`<br>`crud_payment.get_total_unpaid_rent`<br>`crud_lodge.get_room_status_counts`<br>`crud_lodge.get_tenant_counts`<br>`crud_lodge.get_occupied_counts`<br>`crud_room.get_dashboard_rooms` | `Lodge`<br>`Room`<br>`Lease`<br>`Payment`<br>`TenantProfile` | Computes 5 financial metrics (`Potential`, `Expected`, `Collected`, `Unpaid`, `Forecasted`); aggregates occupancy %; buckets rooms into 7 clinical health states (`SAFE`, `EXPIRING`, `OWING`, `OVERDUE`, `PENDING`, `VACANT`, `MAINTENANCE`). |
| **34** | `GET /api/v1/dashboard-landlord/lease-info/{lease_id}` | `dashboard_service.get_dashboard_lease_info` | `crud_lodge.get_room_lease_info` | `Lease`<br>`Room`<br>`TenantProfile`<br>`Payment` | Joins room, lease, tenant user, and payments to render real-time slide-over drawer details. |
| **35** | `GET /api/v1/dashboard-tenant/me/tenants` | `dashboard_service.get_tenant_active_lease_stats` | `crud_lodge.get_tenant_dashboard_stats` | `Lease`<br>`Room`<br>`Payment` | Returns active lease countdown, days remaining, agreed rent, amount paid, and outstanding balance for student portal. |

---

# 🗺️ Master Epic Map

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 LODGEOPS CORE WORKFLOW EPICS                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  EPIC 1: Landlord Onboarding & Portfolio Provisioning                                       │
│  EPIC 2: Cryptographic Tenant Invitation & Triage State Machine                            │
│  EPIC 3: Lease Contract Origination & Upfront Rent Ledger                                  │
│  EPIC 4: Installment Payment Recording & Double-Entry Audit Trail                           │
│  EPIC 5: Move-Out, Voluntary Appeal & Contract Termination Lifecycle                       │
│  EPIC 6: Real-Time Financial Intelligence & Resident Portal Operations                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ EPIC 1: Landlord Onboarding & Portfolio Provisioning

### 📌 User Story 1.1: Landlord Registration & Secure Authentication
> **As a** property owner (Landlord),  
> **I want to** register an account and log in securely,  
> **So that** I can access my private multi-lodge management dashboard.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/users/register/landlord`
  * `POST /api/v1/users/login`
  * `POST /api/v1/users/refresh`
  * `GET /api/v1/users/me`
  * `POST /api/v1/users/logout`

* **End-to-End Orchestration Sequence:**
  ```
  1. Client calls POST /api/v1/users/register/landlord (Email, Password, First/Last Name, Phone)
     └── Database writes User record with hashed password and UserRole.LANDLORD
  2. Client calls POST /api/v1/users/login (OAuth2 Password form: username=email, password)
     └── Backend sets access_token and refresh_token in HttpOnly cookies
  3. Client calls GET /api/v1/users/me (with cookie) ➔ Receives active landlord profile
  4. Periodic refresh: Client calls POST /api/v1/users/refresh ➔ Sliding session rotation
  5. Session termination: Client calls POST /api/v1/users/logout ➔ Revokes refresh token
  ```

---

### 📌 User Story 1.2: Multi-Lodge Portfolio Setup
> **As an** authenticated Landlord,  
> **I want to** create and manage multiple lodge properties,  
> **So that** I can administer student hostels across different campus gates/locations.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/lodges/register`
  * `GET /api/v1/lodges/`
  * `GET /api/v1/lodges/{lodge_id}`
  * `PATCH /api/v1/lodges/{lodge_id}`

---

### 📌 User Story 1.3: Room Inventory Provisioning & Bulk Pricing
> **As an** authenticated Landlord,  
> **I want to** add individual rooms and adjust base rental rates in bulk,  
> **So that** my inventory is accurate and ready for student leasing.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/rooms/`
  * `GET /api/v1/rooms/{lodge_id}/rooms`
  * `GET /api/v1/rooms/{room_id}`
  * `PATCH /api/v1/rooms/{room_id}`
  * `PATCH /api/v1/rooms/{lodge_id}/rooms/bulk`

---

## 💌 EPIC 2: Cryptographic Tenant Invitation & Triage State Machine

### 📌 User Story 2.1: WhatsApp Invite Generation & Token Verification
> **As a** Landlord,  
> **I want to** generate a time-bound cryptographic invite link for my lodge,  
> **And as a** student,  
> **I want to** resolve the link to see which lodge I am joining,  
> **So that** I can register securely without data entry errors or cross-lodge contamination.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/invites/`
  * `GET /api/v1/invites/{invite_id}`

---

### 📌 User Story 2.2: Student Self-Registration via Invite Link
> **As a** prospective student tenant,  
> **I want to** enter my academic details and emergency contacts during signup,  
> **So that** my profile is linked to the lodge and ready for landlord approval.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/users/register/tenant`
  * `GET /api/v1/tenants/profile`
  * `PATCH /api/v1/tenants/profiles/me`

---

### 📌 User Story 2.3: Landlord Review & Application Approval/Rejection
> **As a** Landlord,  
> **I want to** inspect pending student applications and approve or reject them,  
> **So that** unverified or suspicious applicants cannot take possession of my rooms.

* **Endpoints Satisfying This Story:**
  * `GET /api/v1/lodges/{lodge_id}/tenants?status=Pending`
  * `GET /api/v1/tenants/profile/{tenant_id}`
  * `PATCH /api/v1/tenants/{tenant_id}`
  * `DELETE /api/v1/tenants/{tenant_id}`

---

## 📜 EPIC 3: Lease Contract Origination & Upfront Rent Ledger

### 📌 User Story 3.1: Lease Creation with Upfront Payment Invariant
> **As a** Landlord,  
> **I want to** assign an approved tenant to a vacant room and record their initial upfront payment,  
> **So that** an active lease is formed and the room status is updated automatically.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/leases/`
  * `GET /api/v1/rooms/{room_id}`

* **Domain Invariants Verified in Code:**
  1. `amount_paid_upfront <= agreed_rent_amount` (Pydantic `@model_validator` & `can_add_payment`).
  2. `tenant.status == TenantStatus.APPROVED` (raises `UnapprovedTenantError`).
  3. `room.computed_status == RoomStatus.VACANT` (raises `InvalidLeaseActionError` if occupied).
  4. Room and Tenant must belong to the exact same `lodge_id`.

---

### 📌 User Story 3.2: Lease Ledger & Contract History Retrieval
> **As a** Landlord or Tenant,  
> **I want to** query historical and active contracts with flexible status filters.

* **Endpoints Satisfying This Story:**
  * `GET /api/v1/leases/{lodge_id}`
  * `GET /api/v1/leases/tenant/me`
  * `PATCH /api/v1/leases/{lease_id}`

---

## 💳 EPIC 4: Installment Payment Recording & Double-Entry Audit Trail

### 📌 User Story 4.1: Rent Installment Payment with Debt Ceiling Guard
> **As a** Landlord,  
> **I want to** record subsequent rent installments as a student pays down their balance,  
> **So that** the debt ledger accurately tracks remaining receivables without overcrediting.

* **Endpoints Satisfying This Story:**
  * `POST /api/v1/payments/create-payment`
  * `GET /api/v1/payments/{lease_id}`
  * `GET /api/v1/payments/me/{lease_id}`

* **Domain Invariants Verified in Code:**
  1. Lease must not be in `LeaseStatus.TERMINATED` state.
  2. `total_payments + incoming_amt <= agreed_rent_amt` (raises `RentAmtExceededError` on overpayment).
  3. Amount must be strictly positive (`> 0`).

---

## 🚪 EPIC 5: Move-Out, Voluntary Appeal & Contract Termination Lifecycle

### 📌 User Story 5.1: Tenant Voluntary Move-Out Request
> **As an** active student tenant,  
> **I want to** submit a move-out notice when graduating or relocating.

* **Endpoints Satisfying This Story:**
  * `PATCH /api/v1/leases/me/terminate/{lease_id}`

---

### 📌 User Story 5.2: Landlord Lease Termination & Room Reclamation
> **As a** Landlord,  
> **I want to** formally terminate a lease upon student departure,  
> **So that** the room is instantly returned to `VACANT` status.

* **Endpoints Satisfying This Story:**
  * `PATCH /api/v1/leases/terminate/{lease_id}`
  * `GET /api/v1/rooms/{room_id}`

---

## 📊 EPIC 6: Real-Time Financial Intelligence & Resident Portal Operations

### 📌 User Story 6.1: Landlord Financial Intelligence & Action Health Grid
> **As a** Landlord,  
> **I want to** view a real-time financial audit and actionable room health matrix for my lodge.

* **Endpoints Satisfying This Story:**
  * `GET /api/v1/dashboard-landlord/me/landlord/{lodge_id}`
  * `GET /api/v1/dashboard-landlord/lease-info/{lease_id}`

---

### 📌 User Story 6.2: Tenant Resident Portal & Academic Countdown
> **As an** active resident student,  
> **I want to** see how many days are left on my lease and view my remaining rent balance.

* **Endpoints Satisfying This Story:**
  * `GET /api/v1/dashboard-tenant/me/tenants`
