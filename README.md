# LodgeManager API

**A Modern Property & Lodge Management System** built with **FastAPI** and **React** — Designed for efficient management of student accommodations and rental properties in Nigeria.

---

## Table of Contents

- [🚀 Current Status](#-current-status)
- [✨ Features](#-features)
- [🛠 Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
- [📋 Development Roadmap](#-development-roadmap)
- [🤝 Contributing](#-contributing)
- [📞 Contact](#-contact)

---

## 🚀 Current Status

**Active Development** — Finishing touches on **Landlord Dashboard**

- **Backend Completion**: ~85%
- **Frontend Completion**: ~70% (React)

This is my **first major backend project**, built using Just-In-Time (JIT) learning with FastAPI.

---

## ✨ Features

### Backend (FastAPI)

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (**Landlord** & **Tenant**)
  - Secure password hashing with Passlib + Bcrypt

- **Core Business Modules**
  - Lodge / Property Management
  - Room Management
  - Tenant Management
  - Lease & Contract Management
  - Payment Tracking

- **Technical Highlights**
  - Clean Architecture (API → Services → CRUD → Models)
  - SQLAlchemy 2.0 with Alembic migrations
  - Pydantic v2 schemas
  - Dependency Injection
  - Custom exception handling

### Frontend (React)

- Modern React.js frontend (built by collaborator)
- Landlord Dashboard (Currently in active development)
- Tenant Portal (Planned)

---

## 🛠 Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| **Backend** | Python 3.11+, FastAPI               |
| **ORM** | SQLAlchemy 2.0 + Alembic            |
| **Validation** | Pydantic v2                         |
| **Auth** | JWT, Passlib + Bcrypt               |
| **Database** | SQLite (Dev) → PostgreSQL (Target)  |
| **Frontend** | React.js                            |
| **Tools** | Pydantic Settings, Git              |

---

## 📁 Project Structure

```bash
app/
├── api/v1/           # API Routes (v1)
├── core/             # Configuration, Security, Exceptions
├── crud/             # Database CRUD operations
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic request/response models
├── services/         # Business logic layer
├── db/               # Database configuration & session
├── main.py           # Application entry point
└── ...
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js (for frontend)
- PostgreSQL (recommended for production)

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/DonaldXoftDev/LodgeManagerAPIProject.git
cd LodgeManagerAPIProject

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

### Access API Documentation:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📋 Development Roadmap

### Phase 1 (In Progress)
- Complete Landlord Dashboard features
- Polish authentication & authorization
- Improve error handling and validation

### Phase 2 (Next)
- Switch from SQLite to PostgreSQL
- Add comprehensive tests (pytest)
- Docker + Docker Compose setup
- Full integration with React frontend

### Phase 3 (Future)
- Payment gateway integration (Paystack / Flutterwave)
- Email & push notifications
- Analytics & reporting
- Tenant mobile application

---

## 🤝 Contributing

This is my first major backend project. I built it while learning FastAPI on the job (JIT learning).
Feedback, suggestions, and contributions are very welcome!
Feel free to open issues or submit pull requests.

---

## 📞 Contact

**DonaldXoftDev**
Aspiring Backend Developer (Python + FastAPI)
Nigeria
GitHub: [@DonaldXoftDev](https://github.com/DonaldXoftDev)

*Building practical solutions for the Nigerian student housing market.*
*Made with ❤️ for Nigerian landlords and property managers*
