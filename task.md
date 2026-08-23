# Backend Reliability & Payments Roadmap

## The Objective
Resolve 3 critical domain validation and metrics integrity bugs, followed by architectural design and implementation of the end-to-end payment processing pipeline.

---

## Phase 1: Domain Invariant & Metric Bug Fixes

### 1. Landlord Dashboard Tenant Metrics
- **What:** Ensure landlord dashboard metrics only aggregate tenants with `APPROVED` status.
- **Why:** Aggregating unapproved or rejected tenant applicants gives false occupancy numbers and distorts landlord analytics.
- **Affected Layer:** [dashboard_service.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/services/dashboard_service.py) / [landlord_dashboard.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/api/v1/dashboards/landlord_dashboard.py)
- **Status:** ✅ Completed (Verified with automated tests)

### 2. Lease Tenant Status Validation
- **What:** Prevent assigning non-approved tenants to new or active leases.
- **Why:** A lease represents an active contractual occupancy; allowing unapproved tenants breaks the tenant lifecycle state machine.
- **Affected Layer:** [lease_services.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/services/lease_services.py) / [leases.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/api/v1/leases.py)
- **Status:** ✅ Completed (Enforced at Service layer + `UnapprovedTenantError` + Test added)

### 3. Upfront Rent Amount Guardrail
- **What:** Validate that `amount_paid_upfront` cannot exceed the `agreed_rent_amount` during lease creation.
- **Why:** Guard against corrupted financial ledger balances, accidental negative receivables, and improper revenue accounting.
- **Affected Layer:** [lease.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/schemas/lease.py) / [lease_services.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/services/lease_services.py)
- **Status:** ✅ Completed (Pydantic `@model_validator` + Service `can_add_payment` guard)

---

## Phase 2: End-to-End Payment Integration Architecture

### 4. Payment Gateway & Ledger System
- **What:** Design and implement a secure, idempotent payment workflow (Payment initialization, Webhook handling, Transaction verification, Ledger & Receipt generation).
- **Why:** Enable tenants to pay rent/fees digitally while guaranteeing double-entry ledger accuracy and preventing race conditions or replay attacks.
- **Affected Layer:** [payment.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/models/payment.py) / [payment_service.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/services/payment_service.py) / [payments.py](file:///c:/Users/hp/PycharmProjects/LodgeOpsProject/backend/app/api/v1/payments.py)
- **Status:** 🚀 In Progress (Architectural Brainstorming & Design)

---

## Phase 3: Core Feature Backlog & Issues Registry

| Feature / Issue Item | Domain Scope & Architectural Value | Key Entities & Layers | Status |
| :--- | :--- | :--- | :--- |
| **1. Roommate Tracking** | Allow primary leaseholder to link verified student co-tenants/squatters. Ensures fire/occupancy safety and campus security compliance without splitting the legal rent liability. | `TenantProfile`, `Room`, `Lease` | 📋 Backlog |
| **2. Caretaker Scoped Roles** | Multi-tenant lodge delegation: Caretakers can manage specific assigned lodges/rooms (check-in, key handover, inspection) without seeing the Landlord's bank payouts or total portfolio revenue. | `UserRole.CARETAKER`, `LodgeMember`, Policy middleware | 📋 Backlog |
| **3. Lodge Announcements** | Broadcast broadcast feed for landlords/caretakers to push urgent notices (e.g. water pumping times, security curfews, scheduled light maintenance) to tenants via in-app & WhatsApp/SMS. | `Announcement`, `NotificationService` | 📋 Backlog |
| **4. Maintenance Requests** | Ticket lifecycle (`OPEN`, `IN_PROGRESS`, `RESOLVED`) allowing students to report plumbing/electrical faults with photos, and landlords/caretakers to assign artisans and track repair costs. | `MaintenanceTicket`, `TicketComment` | 📋 Backlog |
| **5. Automated Rent Tracking** | Real-time payment gateway integration (Paystack DVA / webhooks), automatic receipt generation, installment tracking, and rent ledger reconciliation. | `Payment`, `PaymentService`, Webhooks | 🚀 In Progress |
| **6. Utility Bills Splitting** | Tracking and billing shared compound utilities (NEPA/EEDC electricity prepaid tokens, generator diesel levies, water pumping tanker fees, waste disposal). | `UtilityBill`, `UtilitySplit` | 📋 Backlog |
| **7. Lodge President & Dues** | Assign a student Lodge President/Representative per lodge with permissions to manage communal sanitation rosters and track recurring student welfare dues. | `LodgePresident`, `LodgeDuesLedger` | 📋 Backlog |
| **8. Annual Subscriptions & Billing** | Landlord annual software license tracking (e.g., ₦4,500/room/year or 1.5% annual license), automated expiry countdown, renewal alerts, and feature-gated PRO capabilities. | `SubscriptionPlan`, `LodgeSubscription` | 📋 Backlog |
| **9. SuperAdmin Command Dashboard** | Global platform mission control: GTV & platform revenue analytics, Paystack stuck-operations escalation queue (`ESC_REF_...`), landlord KYC approval, and sweeper worker monitoring. | `UserRole.SUPERADMIN`, `EscalationTicket`, `PlatformAuditLog` | 📋 Backlog |

