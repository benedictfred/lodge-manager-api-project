# LodgeOps API 🏘️

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)
![Status](https://img.shields.io/badge/Status-Work_in_Progress-orange.svg)
[![GitHub](https://img.shields.io/badge/GitHub-DonaldXoftDev-181717?logo=github)](https://github.com/DonaldXoftDev/LodgeManagerAPIProject)

> **🚧 Work In Progress:** This project is currently in active development (MVP Phase). Core modules like Identity and Property Management are stable, while Lease and Payment orchestration are actively being built.

**LodgeOps** is a comprehensive B2B2C Software-as-a-Service (SaaS) backend designed to digitize and automate the entire property management lifecycle, specifically tailored for student accommodations and multi-unit lodges. 

Built to replace fragmented manual ledgers, messy spreadsheets, and informal messaging apps, this API provides a unified, secure digital ecosystem. It is engineered with an **Outside-In** architectural philosophy, acting as a Backend-For-Frontend (BFF). This ensures that complex database queries and business math are executed entirely on the server, delivering highly optimized, context-aware JSON payloads directly to modern frontend dashboards.

### 🎯 Core Capabilities
* **Frictionless Onboarding:** Self-serve tenant registration via custom landlord invite links, eliminating manual data entry.
* **Portfolio Scaling:** Centralized management for landlords overseeing multiple lodges, complete with real-time room occupancy tracking.
* **Lease Orchestration:** Automated mapping of tenants to physical rooms with strict timeline validation.
* **Digital Financial Ledgers:** Immutable transaction logs that automatically calculate expected revenue versus collected payments to instantly flag outstanding balances.
* **Stateless Security:** Strictly separated, role-based access environments for Landlords and Tenants utilizing JWT (JSON Web Tokens) authentication.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [API Documentation](#api-documentation)
- [Development Roadmap](#development-roadmap)

<a id="tech-stack"></a>
## Tech Stack
* **Framework:** FastAPI
* **Database & ORM:** SQLite (Dev) & SQLAlchemy
* **Migrations:** Alembic
* **Authentication:** OAuth2 with JWT (JSON Web Tokens)
* **Validation & Serialization:** Pydantic
* **Security:** Passlib (Bcrypt)

<a id="project-structure"></a>
## Project Structure

```text
LodgeOpsAPI/
├── alembic/                # Database migration configurations
├── app/                    # Main application source code
│   ├── api/v1/             # Route handlers and endpoints
│   ├── core/               # Application config, exceptions, and security logic
│   ├── crud/               # Database query operations
│   ├── db/                 # Database connection and session management
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic validation models
│   ├── services/           # Business logic and cross-domain orchestration
│   └── main.py             # Application entry point
├── .env.example            # Environment variables template
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

<a id="local-setup"></a>
## Local Setup

### Prerequisites
* Python 3.10+
* Git

### Installation Steps

1. **Clone the repository:**
```bash
git clone [https://github.com/DonaldXoftDev/LodgeManagerAPIProject.git](https://github.com/DonaldXoftDev/LodgeManagerAPIProject.git)
cd LodgeManagerAPIProject
```

2. **Create and activate a virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up Environment Variables:**
Create a `.env` file in the root directory by copying the provided example structure.
```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```
*Make sure your `.env` file contains the following (update values as needed for your local machine):*
```env
# Database Configuration
DATABASE_URL=sqlite:///./lodge_manager.db

# Security & Authentication
SECRET_KEY=your-super-secret-development-key-change-me
```

5. **Run database migrations:**
Initializes the SQLite database and applies the latest schema:
```bash
alembic upgrade head
```

6. **Start the development server:**
```bash
uvicorn app.main:app --reload
```

<a id="api-documentation"></a>
## API Documentation
FastAPI automatically generates interactive API documentation. Once the server is running, navigate to:
* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

<a id="development-roadmap"></a>
## Development Roadmap

### Phase 1: IAM & Core Entities (✅ Complete)
- [x] Base User models and JWT Auth flow
- [x] Landlord Registration
- [x] Self-serve Tenant Registration
- [x] Lodge and Room CRUD operations

### Phase 2: Lease & Financials (🏗️ In Progress)
- [ ] Lease assignment (bridging Tenant and Room)
- [ ] Manual payment logging
- [ ] Lease timeline validation (start/end dates)

### Phase 3: Analytics & BFF (Upcoming)
- [ ] Landlord aggregate financial dashboard endpoint
- [ ] Tenant active status endpoint

---
*Built and Maintained by [Donald Xoft Dev](https://github.com/DonaldXoftDev).* 🚀
