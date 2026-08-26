# 🏢 Lodge Management System: API & User Flow (Source of Truth)

This document is derived directly from the active FastAPI routing and database models. It represents the actual, functional flow of the application.

---

## 1. Authentication & Onboarding (User Flow)

The system uses stateless JWT authentication. Every user (Landlord or Tenant) must authenticate to interact with the API.

### Landlord Onboarding
1. **Register:** `POST /api/v1/auth/register/landlord` - Creates a new user with the `LANDLORD` role.
2. **Login:** `POST /api/v1/auth/login` - Returns the `access_token` and `refresh_token`.

### Tenant Onboarding (Invite System)
Tenants cannot register independently. They must be invited to a specific property.
1. **Generate Invite:** Landlord calls `POST /api/v1/invites/` to create an invite tied to a specific `lodge_id`.
2. **Verify Invite:** Tenant (client app) can optionally call `GET /api/v1/invites/{invite_id}` to verify the link is valid and not expired.
3. **Register via Invite:** Tenant calls `POST /api/v1/auth/register/tenant` using the invite data. This creates their `User` (role: `TENANT`) and automatically generates a `TenantProfile` (status: `PENDING`).
4. **Login:** `POST /api/v1/auth/login` - Returns the JWT.
5. **Approve/Reject:** Landlord calls `POST /api/v1/tenants/{tenant_id}/approve` or `/reject` to finalize the onboarding application and automatically generate the Lease.

---

## 2. Property Management (Landlord Flow)

Landlords set up their portfolio before assigning tenants.

### Lodge Management
1. **Create Lodge:** `POST /api/v1/lodges/register` - Creates a new property.
2. **View Lodges:** `GET /api/v1/lodges/` - Lists all lodges owned by the landlord.
3. **Update Lodge:** `PATCH /api/v1/lodges/{lodge_id}` - Update name/address.

### Room Management
1. **Create Room:** `POST /api/v1/rooms/` - Adds a room to a lodge (sets `room_no`, default `price`).
2. **View Rooms:** `GET /api/v1/rooms/{lodge_id}/rooms` - Lists all rooms in the lodge.
3. **Update Room:** `PATCH /api/v1/rooms/{room_id}` - Update single room details (e.g. status).
4. **Bulk Update:** `PATCH /api/v1/rooms/{lodge_id}/rooms/bulk` - Update multiple rooms at once.

---

## 3. Lease & Occupancy (Landlord Flow)

Once a tenant is registered, approved, and rooms are set up, the landlord can manage leases.

1. **Create Lease:** `POST /api/v1/leases/` - (Also happens automatically on tenant approval). Assigns a `tenant_id` to a `room_id`. Sets the `agreed_rent_amt`, `start_date`, and `end_date`. *(This action automatically changes the Room status to OCCUPIED).*
2. **View Leases:** `GET /api/v1/leases/{lodge_id}` - Lists all leases for a specific property.
3. **Update Lease:** `PATCH /api/v1/leases/{lease_id}` - Modifies active lease terms.
4. **Terminate Lease:** `PATCH /api/v1/leases/terminate/{lease_id}` - Ends the lease, reverting the room status.
5. **Tenant Appeal:** `PATCH /api/v1/leases/me/terminate/{lease_id}` - Tenant voluntarily requests termination.

---

## 4. Financial Tracking (Landlord & Tenant Flows)

Rent collection and payment tracking are tied strictly to the Lease.

### Landlord Perspective
1. **Record Payment:** `POST /api/v1/payments/create-payment` - Logs a payment amount against a specific `lease_id`.
2. **View Lease Payments:** `GET /api/v1/payments/{lease_id}` - Sees all payment history for a tenant's lease.

### Tenant Perspective
1. **View My Payments:** `GET /api/v1/payments/me/{lease_id}` - Tenant can view their own payment history.
2. **View My Leases:** `GET /api/v1/leases/tenant/me` - Tenant can view their active/past lease agreements.
3. **Manage Profile:** `GET /api/v1/tenants/profile` and `PATCH /api/v1/tenants/profiles/me` - View and update their personal contact info.

---

## 5. Analytics & Dashboards

The backend aggregates complex data for the frontend dashboards.

### Landlord Dashboard
* **Endpoint:** `GET /api/v1/dashboard-landlord/me/landlord/{lodge_id}`
* **Data Returned:**
    * **Financials:** Expected Revenue (sum of all active `agreed_rent_amt`), Collected Revenue (sum of all `amount_paid`), Outstanding Balance.
    * **Room Counts:** Total rooms, Occupied, Vacant, Maintenance, Overdue.
    * **Tenant Stats:** Total active tenants.
* **Lease Info Drawer:** `GET /api/v1/dashboard-landlord/lease-info/{lease_id}` - Detailed slide-over pane.

### Tenant Dashboard
* **Endpoint:** `GET /api/v1/dashboard-tenant/me/tenants`
* **Data Returned:** Personal active lease summary, days remaining countdown, and rent balance.
