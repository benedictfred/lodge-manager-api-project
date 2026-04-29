# 📋 Active Task Tracker

## Epic 1: Phase 1 - Identity & Access Management (Landlord Auth)
**Concept Focus:** Authentication, Password Hashing, JWT Statelessness.

### 📝 Pending Tasks
- [x ] **Task 1.4:** Implement secure password hashing utility functions using `passlib`.
- [ x] **Task 1.4.1:** Install `passlib[bcrypt]` and `python-multipart` (if not already in `requirements.txt`).
- [ x] **Task 1.4.2:** Create `app/core/security.py` file.
- [ x] **Task 1.4.3:** Implement `get_password_hash(password: str) -> str` using `bcrypt` in `app/core/security.py`.
- [x ] **Task 1.4.4:** Implement `verify_password(plain_password: str, hashed_password: str) -> bool` using `bcrypt` in `app/core/security.py`.
- [x ] **Task 1.5:** Build the `create_landlord` CRUD operation.
- [ x] **Task 1.5.1:** Create `app/crud/user.py` file.
- [x ] **Task 1.5.2:** Implement `create_user(db: Session, user: UserCreate) -> User` in `app/crud/user.py`. This function should:
    - Hash the `user.password` using `get_password_hash`.
    - Create a new `User` model instance with the hashed password.
    - Add the user to the database session, commit, and refresh.
- [x ] **Task 1.5.3:** Implement `get_user_by_email(db: Session, email: str) -> User | None` in `app/crud/user.py`.
- [x ] **Task 1.6:** Build the `POST /auth/register` API Router.
- [x ] **Task 1.6.1:** Create `app/api/v1/auth.py` file.
- [ x] **Task 1.6.2:** Define a FastAPI `APIRouter` for authentication endpoints.
- [ x] **Task 1.6.3:** Implement the `POST /auth/register` endpoint that:
    - Accepts `UserCreate` schema.
    - Checks if a user with the given email already exists (using `get_user_by_email`). If so, raise `HTTPException(status_code=400, detail="Email already registered")`.
    - Calls `crud.create_user` to create the new user.
    - Returns `UserResponse` of the newly created user.
- [ x] **Task 1.7:** Build the `POST /auth/token` (login) API Router.
- [ x] **Task 1.7.1:** Implement `authenticate_user(db: Session, email: str, password: str) -> User | None` in `app/crud/user.py`. This function should:
    - Get the user by email.
    - Verify the provided password against the hashed password using `verify_password`.
    - Return the user if authenticated, else `None`.
- [ x] **Task 1.7.2:** Implement `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str` in `app/core/security.py`.
- [ ] **Task 1.7.3:** Implement the `POST /auth/token` endpoint that:
    - Accepts `OAuth2PasswordRequestForm` (from `fastapi.security`).
    - Authenticates the user using `authenticate_user`. If not, raise `HTTPException(status_code=401, detail="Incorrect username or password")`.
    - Creates an access token using `create_access_token`.
    - Returns a `Token` schema (e.g., `access_token: str, token_type: str`).
- [ ] **Task 1.8:** Implement `get_current_user` and `get_current_active_user` dependencies.
- [ ] **Task 1.8.1:** Implement `get_current_user(token: str = Depends(oauth2_scheme)) -> User` in `app/api/v1/auth.py` (or `dependencies.py`). This function should:
    - Decode the JWT token.
    - Fetch the user from the database based on the token's subject.
    - Raise `HTTPException(status_code=401, detail="Could not validate credentials")` if invalid.
- [ ] **Task 1.8.2:** Implement `get_current_active_user(current_user: User = Depends(get_current_user)) -> User`. This dependency should check `current_user.is_active`.

### ✅ Completed Tasks
- [x] Review and approve the initial PM System Status Report.
- [x] Ensure project directory, virtual environment, and initial `requirements.txt` are clean and ready.
- [x] **Task 1.1:** Define `User` SQLAlchemy model (Table: `users`).
  - **Fields:** `id` (PK), `email` (Unique, Index), `hashed_password`, `is_active`, `created_at`.
- [x] **Task 1.3:** Create Pydantic schemas for User (`UserCreate`, `UserResponse`), with `password` `max_length` increased to 128.

---
*Note: The PM (AI) will automatically append to this file upon task completion. Do not delete historical items.*