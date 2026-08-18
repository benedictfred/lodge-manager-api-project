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
