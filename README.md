# FinPilot AI

[![CI](https://github.com/prakashpvtech/finpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/prakashpvtech/finpilot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered personal finance & investment platform** — portfolio management, market
research, financial-news intelligence, wealth planning, an AI copilot, and a
document-RAG engine. Built with a **FastAPI** backend and a **Next.js** frontend.

> **Version:** v1.0.0 — feature complete · **Status:** stable / maintenance mode
>
> Designed to be **cloned and run locally**. It is not intended to be hosted as a
> public multi-tenant service.

---

## Table of Contents

- [Overview](#overview)
- [Screens](#screens)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation & Running Locally](#installation--running-locally)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Folder Structure](#folder-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FinPilot AI is a full-stack reference implementation of a modern wealth-management
product. The **backend** owns all business logic (Modules 0–12: identity, AI gateway,
document RAG, market data, analysis, portfolio, news, wealth, dashboard, notifications,
integrations). The **frontend** is presentation-only (features F1–F10) and maps backend
responses to view models. Everything runs locally with SQLite + Redis; PostgreSQL and
third-party data providers are drop-in for a production setup.

## Screens

The app ships these primary views (explore them by running locally and signing up):

- **Dashboard** — net worth, portfolio value, financial-health score, AI insight
- **Portfolio** — holdings, cost basis, realized/unrealized P&L, allocation & growth charts
- **AI Coach** — conversational financial copilot
- **Wealth** — net worth, cash flow, budgeting, AI advice
- **Market** — indices, company search & company pages
- **Settings** — profile, notifications, appearance, integrations

## Features

| Area | What it does |
|------|--------------|
| **Authentication** | JWT auth with short-lived access tokens + refresh-token rotation, Argon2 password hashing, device sessions, brute-force protection, and RBAC (Admin / Premium / Standard). |
| **Dashboard** | Consolidated wealth overview computed from the user's real data, with clean empty states for new accounts. |
| **Portfolio** | Transaction-driven holdings (buy/sell/dividend), cost-basis & P&L, allocation/performance analytics, growth chart. |
| **AI Coach** | Conversational copilot (Google Gemini) with portfolio/news/wealth context; degrades gracefully when unconfigured. |
| **Wealth** | Net-worth tracking, cash flow, budgeting, and AI wealth advice. |
| **Market** | Global indices, company search, company profile/financials/valuation pages. |
| **News** | Financial-news intelligence engine (ingestion, clustering, feeds). |
| **Settings** | Profile, security, notifications, integrations, API keys, appearance. |
| **Notifications** | In-app center with preferences and a background worker. |

Full module map: [`.claude/module-index.md`](.claude/module-index.md).

## Tech Stack

- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2 (async), Alembic, Redis, Pydantic v2, python-jose, Argon2, Google GenAI.
- **Frontend:** Next.js 16 (App Router, React 19, TypeScript), TanStack Query, Zustand, Tailwind CSS v4, ECharts, Framer Motion.
- **Data:** PostgreSQL (production) or SQLite (local). Redis required (rate limiting, brute-force guard, AI memory).
- **Tooling:** pytest, Jest, ESLint, Docker / docker-compose, GitHub Actions CI.

## Architecture

```
┌─────────────┐     HTTP/JSON      ┌──────────────────────────────┐
│  Next.js 16 │ ─────────────────▶ │  FastAPI (Modules 0–12)      │
│  (frontend) │ ◀───────────────── │  auth · AI · RAG · market    │
│ features/   │   axios + JWT      │  analysis · portfolio · news │
│ F1–F10      │   auto-refresh     │  wealth · dashboard · notify │
└─────────────┘                    └───────┬──────────────┬───────┘
                                           │              │
                                    ┌──────▼─────┐  ┌─────▼──────┐
                                    │ PostgreSQL │  │   Redis    │
                                    │ / SQLite   │  │  cache +   │
                                    └────────────┘  │  sessions  │
                                                    └────────────┘
```

The frontend holds no business logic. Deeper design notes:
[`.claude/architecture.md`](.claude/architecture.md).

## Prerequisites

- **Python 3.11**
- **Node.js 20+** (Next.js 16)
- **Redis** running locally (`redis-server`, or `brew services start redis`)
- A database: SQLite works out of the box; PostgreSQL for production.

## Installation & Running Locally

### Quick start (one command)

```bash
redis-server          # in a separate terminal, if not already running
./start-demo.sh       # sets up venv + deps on first run, then starts both servers
```

Then open **http://localhost:3000** and create an account.

### Manual setup

**Backend**

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then edit values (SECRET_KEY must be >= 32 chars)
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export DATABASE_URL="sqlite+aiosqlite:///./finpilot.db"
export REDIS_URL="redis://localhost:6379/0"

python -m app.db.seed         # seed roles
uvicorn main:app --host 0.0.0.0 --port 8000
```

API at http://localhost:8000 (docs `/docs`, health `/health`).

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local     # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App at http://localhost:3000.

## Environment Variables

### Backend (`backend/.env.example`)

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | JWT signing key, **≥ 32 chars**. App exits if missing/weak. |
| `DATABASE_URL` | Yes | `sqlite+aiosqlite:///./finpilot.db` or `postgresql+asyncpg://…`. |
| `REDIS_URL` | Yes | e.g. `redis://localhost:6379/0`. |
| `ENVIRONMENT` | No | `development` / `staging` / `production`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access-token lifetime (default 15). |
| `BACKEND_CORS_ORIGINS` | No | Comma-separated allowed origins. |
| `GEMINI_API_KEY` | No | Enables real AI Coach responses (graceful fallback if unset). |
| `FMP_API_KEY`, `FINNHUB_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `FRED_API_KEY`, `EXCHANGE_RATE_API_KEY` | No | Live market data; a mock adapter is used when unset. |

### Frontend (`frontend/.env.example`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend base URL (inlined at build time). |

> **Never commit real `.env` files or secrets.** Only `.env.example` templates are tracked.

## Testing

| Command | Where | Purpose |
|---|---|---|
| `pytest` | `backend/` | Backend suite (Redis mocked via fakeredis) |
| `npm test` | `frontend/` | Jest suite |
| `npx tsc --noEmit` | `frontend/` | TypeScript typecheck |
| `npm run lint` | `frontend/` | ESLint |
| `npm run build` | `frontend/` | Production build |

## Folder Structure

```
finpilot/
├── backend/                FastAPI application (Python 3.11)
│   ├── app/
│   │   ├── api/            Route handlers
│   │   ├── core/           Config, database, security, RBAC
│   │   ├── models/         SQLAlchemy models
│   │   ├── schemas/        Pydantic schemas
│   │   ├── ai/ agents/     AI gateway + agents
│   │   ├── analysis/ portfolio/ news/ wealth/   Domain engines
│   │   ├── dashboard/ notifications/ integrations/
│   │   └── db/             Seed scripts
│   ├── alembic/           Migrations
│   ├── tests/             pytest suite
│   └── requirements.txt
├── frontend/               Next.js 16 App Router app
│   ├── app/               Routes ((auth) and (dashboard) groups)
│   ├── features/          Feature modules F1–F10 (api/components/hooks/types)
│   ├── components/        Shared UI + layout
│   ├── services/          API client (axios + token refresh)
│   ├── store/             Zustand stores
│   └── __tests__/         Jest tests
├── .claude/               Project documentation (architecture, module index, roadmap)
├── docker-compose.yml
└── start-demo.sh          Local launcher
```

## Roadmap

Planned for future versions (see [`.claude/roadmap.md`](.claude/roadmap.md)):

- Live AI response streaming on the frontend + persistent conversation history
- Real market/news data in production (provider keys) and the remaining analytics endpoints
- Persistent, shared RAG vector store (replace in-memory)
- Real bank/broker integrations beyond mock adapters
- Analysis & Documents workspaces wired to their engines
- Notification delivery channels (email/push) and observability/scale hardening

## Contributing

This is a frozen v1.0 reference project, but improvements are welcome:

1. Fork the repo and create a feature branch (`git checkout -b fix/short-description`).
2. Make your change and keep the suites green: `pytest`, `npm test`, `npx tsc --noEmit`, `npm run lint`, `npm run build`.
3. Follow the existing structure — the frontend stays presentation-only; business logic lives in the backend.
4. Open a pull request describing the change and how you verified it.

Please do not commit secrets, `.env` files, or generated artifacts.

## License

Released under the [MIT License](LICENSE). © 2026 Prakash.
