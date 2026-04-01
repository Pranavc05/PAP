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

## Repository structure

```text
Process Automation/
  README.md
  frontend/
  backend/
```
