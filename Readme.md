# Team Collaboration Hub

A backend platform where users form teams, assign and track work, share files, and get discovered by skill and rating — built with **FastAPI** and **PostgreSQL**.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Table of contents

- [Overview](#overview)
- [Why this project is different](#why-this-project-is-different)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Database migrations](#database-migrations)
- [API overview](#api-overview)
- [Roles & permissions](#roles--permissions)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Overview

Team Collaboration Hub is a role-based backend for building and running project teams end to end: register, build a profile with skills and a CV, create or join a team, get assigned work with due dates, track it to completion, share files, and leave feedback — all under a three-tier moderation structure (superadmin → admins → users).

It's designed to answer a question most simple "team management" clones don't: **how does a team leader actually find the right person, and how does the platform prove someone is good at what they say they're good at?** The rating system, skill-matching search, and activity feed all exist to answer that.

## Why this project is different

Most task-tracker clones stop at "create team, assign task, mark done." This one adds the layer that makes it a genuine *hub*:

- **Ratings are computed, not typed in.** A user's rating comes from actual task completion rate and peer feedback — not a number anyone can set, so it means something when a leader searches by it.
- **Skill-based smart search**, not keyword filtering. Leaders searching for talent get results ranked by skill match + rating + availability, not a flat alphabetical list.
- **Real-time by default.** Notifications, task status changes, and team chat run over WebSockets — leaders see progress live instead of refreshing a dashboard.
- **Two-way team joining.** Leaders can invite; users can also request to join a public team and get approved. Most platforms only build one direction.
- **Built-in accountability.** Every admin action is logged and auditable by the superadmin, and destructive actions default to soft delete — nothing disappears by accident.

## Features

### Superadmin
- Full platform control: manage, suspend, or permanently delete any user, team, or admin
- Reviews the admin audit log — every action an admin takes is recorded

### Admin (x3)
- Manage and moderate users and teams; suspend (reversible) vs. delete (superadmin only)
- Moderation queue for reported users/teams
- Platform analytics: active teams, stale teams, completion-rate trends
- Cannot escalate privileges or act on other admins/superadmin

### Users
- Register/login with JWT auth (access + refresh tokens), email verification, password reset
- Profile: name, photo, bio, skills, CV, website, social links, availability status
- Auto-calculated rating from task completion history + peer feedback
- Dashboard to create or join teams

### Teams
- Create with name, description, min/max member count, and team photo — creator becomes team leader automatically
- Join via unique invite code, or request to join a public team (leader approves)
- Leader can add members by username, remove members, and assign tasks with notes and due dates
- Task status tracking: **not started → in progress → done**, color-coded, with automatic overdue flagging
- Task comment threads for async updates
- Team activity feed — a live log of who did what
- Team visibility: public (discoverable in search) or private (invite/code only)
- Leaders can post open roles; users apply with their CV, leader sends a join request

### Platform-wide
- File sharing per team, with version history
- In-app + real-time notifications and per-team chat (WebSockets)
- Feedback system (on users and on the platform)
- Global search: users search teams, leaders search users by skill/rating/availability
- Gamification badges for milestones (e.g. "5 projects completed")
- Background reminders for approaching deadlines and stale tasks

## Tech stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT (access + refresh), `passlib[bcrypt]` for hashing |
| Real-time | Native FastAPI WebSockets |
| Background jobs | FastAPI `BackgroundTasks` (Celery + Redis if scaling) |
| Search | PostgreSQL `pg_trgm` fuzzy search |
| File storage | Local disk (MVP) → S3-compatible storage later |
| Email | `fastapi-mail` |

## Project structure

```
app/
├── main.py                     # App instance, router mounting, CORS, startup events
├── core/
│   ├── config.py                # Settings via pydantic-settings
│   ├── security.py              # Password hashing, JWT create/verify
│   └── dependencies.py          # get_current_user, require_role() guards
├── db/
│   ├── base.py                  # SQLAlchemy declarative base
│   └── session.py               # Engine + get_db() dependency
├── models/                      # SQLAlchemy ORM models
│   ├── user.py
│   ├── team.py
│   ├── task.py
│   ├── file.py
│   ├── notification.py
│   └── feedback.py
├── schemas/                     # Pydantic request/response schemas
├── crud/                        # DB read/write functions
├── services/                    # Business logic (rating calc, matching, email)
├── api/v1/
│   ├── auth.py
│   ├── users.py
│   ├── teams.py
│   ├── tasks.py
│   ├── admin.py
│   ├── search.py
│   ├── files.py
│   ├── feedback.py
│   ├── notifications.py
│   └── ws.py                    # WebSocket endpoint
└── utils/
alembic/                          # Migration scripts
tests/
.env
requirements.txt
```

## Getting started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- `pip` and a virtual environment tool

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/team-collaboration-hub.git
cd team-collaboration-hub

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your values
cp .env.example .env
```

### Run the app

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## Environment variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql+asyncpg://user:pass@localhost:5432/team_hub` |
| `SECRET_KEY` | Secret used to sign JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token lifetime |
| `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_FROM` | SMTP credentials for verification/reset emails |
| `UPLOAD_DIR` | Local path for uploaded files (MVP storage) |

## Database migrations

```bash
# Generate a migration after changing a model
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head
```

Run a migration every time a model changes — don't let the database schema drift from the code.

## API overview

| Group | Base path | Handles |
|---|---|---|
| Auth | `/api/v1/auth` | Register, login, refresh, password reset |
| Users | `/api/v1/users` | Profile CRUD, skills, CV, availability |
| Teams | `/api/v1/teams` | Create, join, join requests, member management |
| Tasks | `/api/v1/tasks` | Assign, update status, comments |
| Files | `/api/v1/files` | Upload, list, download, version history |
| Notifications | `/api/v1/notifications` | In-app notifications |
| WebSocket | `/api/v1/ws` | Live chat and real-time updates |
| Search | `/api/v1/search` | User and team search |
| Feedback | `/api/v1/feedback` | Submit and view feedback |
| Admin | `/api/v1/admin` | Moderation, suspension, analytics, audit log |

Full interactive documentation is auto-generated by FastAPI at `/docs` (Swagger UI) and `/redoc`.

## Roles & permissions

| Role | Scope |
|---|---|
| **Superadmin** | Full access — manage/suspend/delete any user, team, or admin; view audit log |
| **Admin** | Manage/suspend users and teams; moderate reports; view analytics — cannot touch other admins |
| **Team leader** | Assigned automatically to the team creator; manage members, assign tasks, post recruitment openings |
| **Team member** | Update assigned task status, comment, view team dashboard |

## Roadmap

- [ ] Gamification badges
- [ ] Exportable team performance reports (PDF/CSV)
- [ ] File versioning
- [ ] Rate limiting on join requests/invites
- [ ] Elasticsearch migration if search volume outgrows `pg_trgm`

## Contributing

This is currently a solo learning/portfolio project. Issues and suggestions are welcome — open an issue describing the change before submitting a pull request.

## License

MIT — free to use, modify, and learn from.

Hasnain Sharif.