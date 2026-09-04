# Backend Architecture & Agent Brain Map (`brain.md`)

This document serves as the **Central Brain & Architectural Blueprint** for the Team Collaboration Hub backend codebase. Any AI Agent (including Antigravity, Gemini, or Claude) or developer modifying this project **MUST** consult this document to understand the application flow, file organization, and architectural conventions.

---

## 1. Executive Summary & Tech Stack

- **Framework**: FastAPI (Asynchronous Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM & Driver**: SQLAlchemy 2.0 (Async) + `asyncpg` + `greenlet`
- **Settings & Config**: `pydantic-settings` (v2) with dynamic `.env` path resolution
- **Data Validation**: Pydantic v2 + `email-validator`
- **Authentication**: JWT (Access + Refresh tokens) via `python-jose`, password hashing via `bcrypt`
- **Migrations**: Alembic (Async runner configuration)
- **Real-Time Communication**: Native FastAPI WebSockets (`/ws`)

---

## 2. System Architecture & Request Lifecycle

```
HTTP Request / WebSocket
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ app/main.py (FastAPI App)                                  │
│ - Lifespan Handler (Async Engine Shutdown Cleanup)           │
│ - CORS Middleware Configuration                             │
│ - Router Dispatcher (/api/v1/auth, /api/v1/users, etc.)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ app/core/dependencies.py & app/db/session.py                │
│ - Auth Guard (JWT Verification via app/core/security.py)    │
│   • get_current_user -> extracts token, fetches User model │
│   • get_current_active_user -> verifies is_active = True    │
│   • require_role("admin", ...) -> verifies role permissions │
│ - Database Dependency: get_db() -> AsyncSession             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ app/api/v1/*.py (Route Handlers)                            │
│ - Validate Incoming Payloads via app/schemas/*.py           │
│ - Invoke Business Logic via app/services/*.py               │
│ - Execute Database Queries via app/crud/*.py                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ app/models/*.py & app/db/base.py                            │
│ - SQLAlchemy Declarative ORM Models mapped to PostgreSQL    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive File & Folder Map

```
backend/
├── .env                       # Environment variables (DATABASE_URL, SECRET_KEY, ALGORITHM, etc.)
├── requirements.txt           # Dependency requirements manifest
├── brain.md                   # [THIS FILE] Project brain, architecture, and agent instructions
├── alembic.ini                # Alembic root migration configuration
├── alembic/                   # Database migration configuration and revisions
│   ├── env.py                 # Async Alembic runner (connects via create_async_engine)
│   ├── script.py.mako         # Migration script template
│   └── versions/              # Individual migration revision scripts
├── tests/
│   └── test_phase2_auth_profiles.py # Integration test suite for Phase 2 Auth and Profiles
└── app/
    ├── main.py                # Main FastAPI entrypoint, lifespan context, CORS middleware, routes
    ├── core/
    │   ├── config.py          # Pydantic BaseSettings loading .env, database URL validator
    │   ├── security.py        # Bcrypt password hashing & JWT token generation/decoding (access, refresh, reset)
    │   └── dependencies.py    # Common API dependencies (get_current_user, get_current_active_user, require_role)
    ├── db/
    │   ├── base.py            # SQLAlchemy DeclarativeBase base class
    │   ├── session.py         # Async engine (create_async_engine), AsyncSessionLocal, get_db() generator
    │   └── __init__.py        # Database package exports (Base, engine, AsyncSessionLocal, get_db)
    ├── models/                # SQLAlchemy Database ORM Models
    │   ├── user.py            # User profile (id, email, hashed_password, role, name, bio, skills, cv, links, availability, is_active, rating [read-only])
    │   ├── team.py            # Team profile, invite code, leader ID, visibility
    │   ├── task.py            # Task assignment, status (not_started, in_progress, done), due date
    │   ├── file.py            # File attachments, versions, team association
    │   ├── notification.py    # In-app notifications
    │   └── feedback.py        # Peer feedback & platform feedback
    ├── schemas/               # Pydantic v2 Request & Response Data Validation Schemas
    │   ├── auth.py            # LoginRequest, TokenResponse, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm
    │   ├── user.py            # UserCreate, UserProfileUpdate, UserAdminUpdate, UserResponse, UserRole, AvailabilityStatus
    │   ├── team.py            # TeamCreate, TeamUpdate, TeamResponse schemas
    │   ├── task.py            # TaskCreate, TaskStatusUpdate, TaskResponse schemas
    │   └── file.py            # FileUpload, FileResponse schemas
    ├── crud/                  # Direct Database Read/Write Query Functions
    │   ├── user.py            # CRUD operations for User (get_user, get_user_by_email, create_user, update_user_profile, update_password, list_users)
    │   ├── team.py            # CRUD operations for Team model
    │   └── task.py            # CRUD operations for Task model
    ├── api/v1/                # Endpoint Controllers (Prefix: /api/v1)
    │   ├── auth.py            # POST /register, POST /login, POST /login/token, POST /refresh, POST /forgot-password, POST /reset-password
    │   ├── users.py           # GET /me, PUT /me, PATCH /me, GET /{user_id}, GET /
    │   ├── teams.py           # Team CRUD, join requests, member management routes
    │   ├── tasks.py           # Task assignment, status update routes
    │   ├── files.py           # File upload, download, versioning routes
    │   ├── notifications.py   # User notification list & read state routes
    │   ├── search.py          # Skill-matching & team discovery routes
    │   ├── feedback.py        # Peer & platform feedback submission routes
    │   ├── admin.py           # Superadmin & Admin moderation / analytics routes
    │   └── ws.py              # WebSocket endpoint for real-time updates & team chat
    ├── services/              # Complex Domain Logic & Background Services
    └── utils/                 # Helper utilities and formatting functions
```

---

## 4. Key Module Breakdown & Implementation Details

### Core & Configuration
- **`app/core/config.py`**:
  - Uses `pydantic-settings` `BaseSettings`.
  - Automatically locates `.env` via `Path(__file__).resolve().parent.parent.parent / ".env"`.
  - Automatically transforms `postgresql://` or `postgresql+psycopg2://` URIs into `postgresql+asyncpg://`.
- **`app/core/security.py`**:
  - Direct `bcrypt` hashing avoiding passlib wrap bug on modern Python/bcrypt releases.
  - Generates JWT Access tokens (short-lived) and Refresh tokens (7 days).
  - Generates and verifies secure password reset tokens.
- **`app/core/dependencies.py`**:
  - `get_current_user`: Validates JWT Bearer token and returns active ORM `User` instance.
  - `get_current_active_user`: Guards against inactive accounts.
  - `require_role(*allowed_roles)`: Role-based authorization dependency factory.
- **`app/db/session.py`**:
  - Initializes `create_async_engine(settings.DATABASE_URL)`.
  - Uses `async_sessionmaker` with `expire_on_commit=False`.
  - Provides `get_db()` async generator yielding `AsyncSession`.
- **`app/main.py`**:
  - Configures `lifespan` context manager executing `await engine.dispose()` on server shutdown for instant `Ctrl+C` termination.
  - Mounts `CORSMiddleware` using `settings.CORS_ORIGINS`.
  - Serves health check at `/health` (`SELECT 1` database query).

### Phase 2: Auth & Profiles Implementation
- **User ORM Model (`app/models/user.py`)**:
  - `id`: Integer PK
  - `email`: String(255) unique indexed
  - `hashed_password`: String(255)
  - `role`: String(50) default `"user"` (`superadmin`, `admin`, `user`)
  - `name`: String(255)
  - `profile_pic`: String(500)
  - `bio`: Text
  - `skills`: JSON default `[]`
  - `cv_url`: String(500)
  - `website`: String(255)
  - `social_links`: JSON default `{}`
  - `availability`: String(50) default `"available"` (`available`, `busy`, `unavailable`)
  - `is_active`: Boolean default `True`
  - `rating`: Float default `0.0` (**read-only for user**, computed in Phase 4)
  - `created_at`, `updated_at`: DateTime timezone-aware
- **Auth Endpoints (`app/api/v1/auth.py`)**:
  - `POST /api/v1/auth/register` (Creates user, returns `UserResponse`, 201 Created)
  - `POST /api/v1/auth/login` (JSON login, returns access + refresh tokens)
  - `POST /api/v1/auth/login/token` (OAuth2 form-data for Swagger UI Authorize button)
  - `POST /api/v1/auth/refresh` (Refreshes token pair)
  - `POST /api/v1/auth/forgot-password` (Issues password reset token)
  - `POST /api/v1/auth/reset-password` (Verifies reset token and updates password)
- **User Profile Endpoints (`app/api/v1/users.py`)**:
  - `GET /api/v1/users/me` (Returns authenticated user profile)
  - `PUT /api/v1/users/me` & `PATCH /api/v1/users/me` (Updates profile details; rating is immutable)
  - `GET /api/v1/users/{user_id}` (Public profile lookup by user ID)
  - `GET /api/v1/users/` (List users with `skip` and `limit` pagination)

---

## 5. Mandatory Agent Update Protocol (Sync Rule)

> [!IMPORTANT]
> **AGENT DIRECTIVE FOR MAINTAINING `brain.md`**:
> Whenever an AI Agent or developer performs ANY of the following actions in the backend codebase, they **MUST** immediately update `backend/brain.md` to keep this brain map in 100% sync:
> 
> 1. **New File or Directory**: Add the file path and its responsibility to Section 3 (*Comprehensive File & Folder Map*).
> 2. **Database Schema / Model Change**: Update Section 3 & 4 under `app/models/` detailing the new fields or model entities.
> 3. **New API Route / Endpoint**: Update `app/api/v1/` section describing the new controller endpoints and their purpose.
> 4. **New Dependency / Config Option**: Update Section 1 & 4 and Section 3 under `app/core/config.py` or `.env`.
> 5. **Architectural Change**: Update Section 2 (*System Architecture & Request Lifecycle*) if request flow or middleware alters.

---

## 6. How to Run & Verify

```powershell
# Navigate to backend
cd backend

# Activate Virtual Environment
.venv\Scripts\activate

# Run Database Migrations
alembic upgrade head

# Run API Server
uvicorn app.main:app --reload

# Run Phase 2 Integration Tests
python tests/test_phase2_auth_profiles.py

# Verification Endpoints
# Root API: http://127.0.0.1:8000/
# Health Check: http://127.0.0.1:8000/health
# Swagger Docs: http://127.0.0.1:8000/docs
```
