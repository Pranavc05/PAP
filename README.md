# AI EdTech Platform for Process Automation

This repository contains the initial MVP scaffold for an interactive learning platform focused on process automation and AI-driven workflow design.

## Current scope (starter build)

- `frontend/`: Next.js app scaffold with starter pages
- `backend/`: FastAPI app scaffold with health and curriculum endpoints
- Shared conventions for rapid MVP development

## MVP features to implement next

1. Authentication and learner onboarding
2. Level 1 course content and quiz engine
3. Workflow builder with node simulation
4. AI tutor chat with Socratic coaching mode
5. Case-study driven project flow and progress tracking

## Local development

## Environment setup

### Backend env

```bash
cd backend
cp .env.example .env
```

### Frontend env

```bash
cd frontend
cp .env.example .env.local
```

You can keep defaults for now. As we add database/auth/AI integrations, fill the relevant keys.

## Database and migrations

The backend now persists workflows in SQL (SQLite by default for local development).

Run migrations:

```bash
cd backend
alembic upgrade head
```

If you switch to Postgres, update `DATABASE_URL` in `backend/.env` before running migrations.

## Authentication modes

Backend auth is provider-driven through `AUTH_PROVIDER`:

- `dev` (default): accepts `X-Dev-User-Id` header for local testing
- `supabase`: verifies bearer JWT tokens using Supabase JWKS
- `oidc`: verifies bearer JWT tokens using generic OIDC JWKS config (AWS/GCP/Azure compatible)

For frontend local dev:

- keep `NEXT_PUBLIC_AUTH_MODE=dev` to test quickly
- set `NEXT_PUBLIC_AUTH_MODE=supabase` or `NEXT_PUBLIC_AUTH_MODE=oidc` and paste an access token in Workflow Lab to test protected routes
- use `/login` to create/update your local frontend session state

For `oidc`, set these backend env values:

- `AUTH_JWKS_URL`
- `AUTH_JWT_ISSUER`
- `AUTH_JWT_AUDIENCE` (optional if your provider does not use audience checks)
- `AUTH_JWT_ALGORITHMS` (comma-separated, defaults to `RS256`)

If your SQLite DB was created before auth columns were added, delete `backend/process_automation.db` and run migrations again.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend should run on `http://localhost:3000` and call backend APIs at `http://localhost:8000`.

## API endpoints included

- `GET /health`
- `GET /api/v1/levels`
- `GET /api/v1/projects/starter`
- `GET /api/v1/courses`
- `GET /api/v1/courses/{course_id}`
- `GET /api/v1/lessons/{lesson_id}`
- `POST /api/v1/lessons/{lesson_id}/complete`
- `GET /api/v1/courses/{course_id}/progress`
- `GET /api/v1/lessons/{lesson_id}/quiz`
- `POST /api/v1/lessons/{lesson_id}/quiz/submit`
- `GET /api/v1/lessons/{lesson_id}/quiz/attempts`

## Repository structure

```text
Process Automation/
  README.md
  frontend/
  backend/
```
