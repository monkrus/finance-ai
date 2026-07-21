# FinPilot AI — Project Guide for Claude

FinPilot AI is an AI-powered personal finance & investment platform: portfolio
management, market research, financial news intelligence, wealth planning, an AI
copilot, and a document-RAG engine — a FastAPI backend (Modules 0–12) and a
Next.js frontend (Modules F1–F10).

This file is the entry point for any Claude session. Detailed docs live in
[`.claude/`](.claude/) — start with [`.claude/architecture.md`](.claude/architecture.md)
and [`.claude/module-index.md`](.claude/module-index.md).

---

## Status

FinPilot **v1.0.0** is feature-frozen and stable: the backend and frontend test
suites pass, TypeScript and ESLint are clean, and the production build succeeds.
See [`.claude/changelog.md`](.claude/changelog.md) for release history and
[`.claude/roadmap.md`](.claude/roadmap.md) for deferred/planned work.

When in doubt, trust the code over any doc claim.

---

## Repository layout

```
finpilot/
├── backend/          FastAPI app (Python 3.11), Modules 0–12
├── frontend/         Next.js 16 App Router (React 19, TS), Modules F1–F10
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Run locally

Requires **Redis** (rate limiter + brute-force guard + AI memory) and a database
(Postgres, or SQLite for local/dev).

```bash
# Backend  (needs SECRET_KEY >= 32 chars, mandatory or the app exits)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # NOTE: file is missing in this repo (see above)
export SECRET_KEY="<32+ char secret>" \
       DATABASE_URL="sqlite+aiosqlite:///./finpilot.db" \
       REDIS_URL="redis://localhost:6379/0" ENVIRONMENT=development
python -m app.db.seed                     # seed roles (Admin / Premium User / Standard User)
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev   # http://localhost:3000
```

- Backend: http://localhost:8000  (docs `/docs`, health `/health`)
- Frontend: http://localhost:3000

## Test / verify

| Command | Where | Purpose |
|---|---|---|
| `pytest` | `backend/` | Backend suite (needs Redis mocked via fakeredis in conftest) |
| `npm test` | `frontend/` | Jest suite |
| `npx tsc --noEmit` | `frontend/` | TypeScript typecheck |
| `npm run build` | `frontend/` | Production build |
| `npm run lint` | `frontend/` | ESLint |

## Coding rules for Claude in this repo

- **Do not redesign** the architecture or module boundaries (backend Modules 0–12,
  frontend features `F1–F10`). Fix within the existing structure.
- **Frontend is presentation-only.** Business logic lives in the backend. The
  frontend maps backend responses to view models in `features/<module>/api/`.
- **Never fabricate financial data.** Widgets must derive from authenticated user
  data or show empty states.
- **Use only existing backend endpoints** unless explicitly asked to add one.
  Adapt the frontend to the real contract in the `api/` layer.
- Preserve passing tests; add tests for new behavior; keep `tsc` and the build green.
- Convert relative dates to absolute in docs. Keep these `.claude/` docs updated as
  the source of truth for future sessions.

## Where to look

| Need | File |
|---|---|
| Overview, stack, standards | [`.claude/context.md`](.claude/context.md) |
| How it all fits together | [`.claude/architecture.md`](.claude/architecture.md) |
| Per-module file/API/model map | [`.claude/module-index.md`](.claude/module-index.md) |
| What's done / in progress / planned | [`.claude/roadmap.md`](.claude/roadmap.md) |
| Active tasks | [`.claude/current-sprint.md`](.claude/current-sprint.md) |
| History of changes | [`.claude/changelog.md`](.claude/changelog.md) |
