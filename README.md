# AI-powered personal finance & investment platform

Portfolio management, market research, financial-news intelligence, wealth planning, an AI copilot, and a document-RAG engine. Built with a **FastAPI** backend and a **Next.js** frontend.

---

## Assessment Summary

This repo contains a completed AI Engineer technical assessment. All work lives
on the **`git-assessment`** branch (the default). Here is what was done and where
to find it.

### What was built

| Task | What | Where |
|------|------|-------|
| **Task 1 — Architecture Review** | Ten architectural improvements, prioritised by production urgency. Covers authorization (IDOR), prompt versioning, evaluation, model routing, observability, memory, caching, guardrails, composition, and orchestration. Each includes the current limitation, a proposed fix, expected benefits, and trade-offs. | [`docs/01-architecture-review.md`](docs/01-architecture-review.md) |
| **Task 2 — Investment Strategy Agent** | A new agent that reviews a portfolio, builds an investment strategy, and grounds every claim in retrieved context. Includes schemas, context assembly, structured generation, post-hoc grounding validation, an API endpoint, and 19 tests. | Code: `backend/app/agents/`, `backend/app/api/v1/agents.py`, `backend/app/schemas/investment_strategy.py` · Design notes: [`docs/02-implementation-notes.md`](docs/02-implementation-notes.md) |
| **Task 3 — RAG Review** | Review of the existing retrieval pipeline. Identifies concrete defects (in-memory vector store, broken keyword search, silent embedding failures, destroyed tables) and proposes a replacement architecture with reranking, BM25, and a three-tier evaluation plan. | [`docs/03-rag-review.md`](docs/03-rag-review.md) |
| **Task 4 — Git Challenges** | Recovered a lost commit (reflog), moved a misplaced payment commit to `feature/payment` (cherry-pick + rebase), and cleaned up six self-cancelling typo commits (interactive rebase → empty → dropped). | [`docs/04-git-challenges.md`](docs/04-git-challenges.md) |

### How to verify

```bash
# Run the test suite (no infrastructure needed — uses mocks)
cd backend && python -m pytest

# Check the commit history
git log --oneline

# Confirm the payment branch exists
git log --oneline feature/payment -2

# See all files changed vs the original
git diff --stat main git-assessment
```

### Branch layout

| Branch | Purpose |
|--------|---------|
| `git-assessment` (default) | All assessment work — 9 commits over the cleaned base |
| `feature/payment` | Payment commit relocated here (Git Challenge 3) |
| `main` | Original upstream code, untouched |

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

## Tech Stack

- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2 (async), Alembic, Redis, Pydantic v2, python-jose, Argon2, Google GenAI.
- **Frontend:** Next.js 16 (App Router, React 19, TypeScript), TanStack Query, Zustand, Tailwind CSS v4, ECharts, Framer Motion.
- **Data:** PostgreSQL (production) or SQLite (local). Redis required (rate limiting, brute-force guard, AI memory).

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

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** (Next.js 16)
- **Redis** running locally (`redis-server`, or `brew services start redis`)
- A database: SQLite works out of the box; PostgreSQL for production.

## Installation & Running Locally

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
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

---

## Investment Strategy Agent

A specialized agent for long-term investment planning. It reviews a portfolio,
discusses asset allocation and diversification, explains risk, and frames a
multi-year plan — grounded in retrieved context rather than generated from the
model's priors.

### Endpoint

```
POST /api/v1/agents/investment-strategy
Authorization: Bearer <access token>
```

The unversioned path `POST /agents/investment-strategy` is registered as an
alias to the same handler.

```jsonc
// request
{
  "portfolio_id": 1,
  "profile": {
    "risk_tolerance": "moderate",      // conservative | moderate | aggressive
    "time_horizon_years": 20,
    "experience_level": "beginner",    // beginner | intermediate | advanced
    "goals": ["retire at 60"],
    "constraints": ["no tobacco"]
  },
  "question": "Am I too concentrated in tech?",  // optional
  "include_documents": true,
  "max_holdings": 8
}
```

The response separates retrieved fact from model interpretation. Each section
carries `grounded_findings` (statements with `refs` into the retrieved context)
and `generated_insights` (interpretation, explicitly not retrieved fact), plus
top-level `assumptions`, `data_gaps`, `sources`, `confidence` and `validation`.

### Grounding

Context is assembled deterministically from the existing services — portfolio
analytics and holdings, company profiles and ratios, market news, and the user's
uploaded filings via RAG — with each source addressable as `PORTFOLIO-1`,
`COMPANY-2`, `NEWS-1`, `DOCS-1`, `PROFILE-1`.

After generation the server validates the answer against that context: findings
whose citations do not resolve are dropped, partially valid citations are
narrowed to the refs that hold up, and the model's self-reported `confidence` is
treated as a ceiling candidate rather than a result. A failing data source
becomes a visible entry in `data_gaps` instead of a silent hole or a 500.

Portfolio ownership is verified against the authenticated user before any
holding is read, and document retrieval is always scoped to the caller.

### Tests

```bash
cd backend && python -m pytest
```

### Assessment write-ups

- [`docs/01-architecture-review.md`](docs/01-architecture-review.md) — architecture review
- [`docs/02-implementation-notes.md`](docs/02-implementation-notes.md) — design decisions and prompt engineering strategy
- [`docs/03-rag-review.md`](docs/03-rag-review.md) — RAG review
- [`docs/04-git-challenges.md`](docs/04-git-challenges.md) — Git challenge walkthrough
