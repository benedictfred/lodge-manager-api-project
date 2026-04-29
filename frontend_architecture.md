# Lodge Management System: Frontend Architecture & UI/UX Plan

## 1. System Overview (The "Where" and "How")
*   **Where it lives:** The frontend will be a decoupled Client-Side Application (React.js, Vue, or Vanilla JS) running in the user's browser.
*   **How it connects:** It will consume JSON data from the FastAPI backend via asynchronous `fetch` or `axios` requests to the `/api/v1/` endpoints.
*   **The Goal:** To translate the underlying SQLAlchemy relational data (`Room`, `Tenant`, `Lease`, `Payment`) into a modern, actionable SaaS dashboard for the Landlord to track occupancy, lease timelines, and revenue.

## 2. Global UI/UX Features
*   **Design Aesthetic:** Modern, clean SaaS interface. Minimalist borders, soft shadows (glassmorphism), and clear typography.
*   **Theme Management:** System-wide Light and Dark mode toggle via CSS variables.
*   **Responsiveness:** Fluid grid layouts that adapt from 4-columns on desktop down to a single column on mobile devices.
*   **Tailwind Color Palette Rules (The Vibe):**
    *   *Backgrounds:* Use blended, soft gradients (e.g., `bg-gradient-to-br from-blue-50 to-indigo-100`).
    *   *Glassmorphism:* Cards and Navbars should be slightly transparent with blur (e.g., `bg-white/70 backdrop-blur-md`).
    *   *Text:* Use deep, rich shades (e.g., `text-indigo-900`) instead of pure black.
    *   *Semantic Status Badges (The "Pastel Pill" effect):*
        *   **Vacant (Ash):** `bg-gray-100/80 border-gray-200 text-gray-600`
        *   **Occupied/Safe (Green):** `bg-emerald-50/80 border-emerald-200 text-emerald-700`
        *   **Maintenance/Expiring (Yellow):** `bg-amber-50/80 border-amber-200 text-amber-700`
        *   **Overdue (Red):** `bg-rose-50/80 border-rose-200 text-rose-700`

## 3. Core Dashboard Components

### A. Top Navigation Shell
*   **Left:** Branding/Logo (LodgeManager).
*   **Center:** Main generic navigation links (Dashboard, Rooms, Tenants, Payments, Settings).
*   **Right:** Dark mode toggle and Landlord Profile (Avatar, Name, Role).

### B. Financial Metrics Banner
*   **Purpose:** High-level revenue tracking.
*   **Expected Revenue:** Sum of all `agreed_rent_amt` from active leases.
*   **Collected Revenue:** Sum of all `amount_paid` (derived from Payment tables).
*   **Outstanding Balance:** Mathematical difference colored in red to draw attention.

### C. The Interactive Room Grid
*   **Filtering System:** segmented controls filtering the grid state by derived lease timelines:
    *   ⚪ **Vacant:** No active lease.
    *   🟢 **Safe:** Lease end date is > 90 days away.
    *   🟡 **Expiring Soon:** Lease ends in < 90 days.
    *   🔴 **Overdue:** Lease end date has passed.
*   **Room Cards (The Grid Items):**
    *   Displays `room_no` prominently.
    *   Visual Status Badge (Color-coded based on the semantic rules above).
    *   Displays current Tenant name (or "No active lease").
    *   Mini Progress Bar: A visual timeline showing the percentage of the lease duration completed.

### D. The Slide-Out Context Panel
*   **Trigger:** Clicking any Room Card slides the panel in from the right (position: fixed, right-aligned).
*   **State Management:** Swaps between "Room View" and "Tenant View" without closing the panel.
*   **Room View Data:**
    *   **Lease Timeline:** Start Date, End Date, and exact "Days Remaining".
    *   **Financial Breakdown:** Agreed Rent, Amount Paid, and Outstanding Balance.
    *   **Tenant Quick-Card:** A clickable mini-profile of the current occupant.
    *   **Action Buttons:** Context-aware buttons (e.g., a Red "Send Overdue Notice" button if the status is OVERDUE, hidden if SAFE).
*   **Tenant Profile View:**
    *   Accessed by clicking the Tenant Quick-Card.
    *   Displays deep-dive contact info (Email, Phone) matching the `TenantBase` schema.
    *   Includes a "Back to Room" navigation button.

## 4. Backend Data Mapping
The frontend relies heavily on a joined payload structure. The frontend developer should expect a nested JSON response similar to this logic:
*   `GET /api/v1/rooms/` should return the Room model.
*   If `status == 'Occupied'`, the payload should nest the active Lease object.
*   The Lease object should nest the associated Tenant object.
*   *Note for Frontend Dev:* The "Days Left" and "Status Colors" (Safe, Expiring, Overdue) should be dynamically calculated on the frontend using the `Lease.end_date` vs `Date.now()`.

## 5. Developer Polish & Animation Requests (Future Scope)
*   **Skeleton Loaders:** When fetching data from the FastAPI backend, display pulsing skeleton shapes in the grid instead of a blank white screen.
*   **Toast Notifications:** When an Action Button is clicked (like "Send Reminder" or "Assign Tenant"), trigger a non-blocking slide-in notification at the bottom of the screen instead of native browser `alert()` boxes.
*   **Smooth Transitions:** Use libraries like Framer Motion (if React) to animate the grid items reshuffling when a filter is clicked, rather than having them instantly snap in and out of existence.