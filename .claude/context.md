# Context

## Project overview

**FinPilot AI** is an AI-powered personal finance and investment platform. It
unifies, in one workspace:

- **Portfolio management** — holdings, allocation, performance, risk analytics, transactions.
- **Market intelligence** — quotes, fundamentals, ratios, valuation, earnings.
- **News intelligence** — curated market news with sentiment and portfolio impact.
- **Wealth management** — net worth, cash flow, budgets, goals, financial planning, AI coach.
- **AI Copilot** — a chat assistant with agent routing and tool use.
- **Document intelligence (RAG)** — upload financial documents, ask grounded questions.
- **Notifications**, **integrations** (banks/brokers, import/export), **settings/admin**, **RBAC**.

The system is delivered as two deployables:

- **Backend** — FastAPI, "Modules 0–12" (identity/auth, market data, AI gateway,
  document RAG, analysis, portfolio, news, wealth, dashboard, notifications, integrations).
- **Frontend** — Next.js App Router, "Modules F1–F10" (auth, dashboard, portfolio,
  market, news, wealth, AI, notifications, settings/integrations).

> Status: this repo holds the **v1.0 RC1** build. See `changelog.md` and
> `current-sprint.md` for what is done vs. outstanding (and the working-copy
> divergence noted in `CLAUDE.md`).

## Tech stack

### Backend (`backend/`)
- **Python 3.11**, **FastAPI**, **Starlette** (session + custom middleware).
- **SQLAlchemy 2.0 async** ORM + **Alembic** migrations. Drivers: `asyncpg`
  (Postgres) / `aiosqlite` (SQLite for tests/local).
- **Redis** (`redis.asyncio`) — rate limiting (`fastapi-limiter`), brute-force
  lockout, and AI conversation memory.
- **Security** — `passlib[argon2]` password hashing, `python-jose` JWT access
  tokens, opaque rotating refresh tokens, RBAC.
- **AI** — Google **Gemini** via `google-genai` (`gemini-2.5-flash`), behind an
  internal AI Gateway abstraction; `tenacity` for retries.
- **Market data** — pluggable adapters (FMP, Finnhub, AlphaVantage, FRED,
  ExchangeRate, EDGAR) with a **MockAdapter** fallback when API keys are absent.
- **Testing** — `pytest`, `pytest-asyncio`, `fakeredis`; ~60 test files.

### Frontend (`frontend/`)
- **Next.js 16** (App Router, Turbopack), **React 19**, **TypeScript**.
- **Tailwind CSS v4** (via `@tailwindcss/postcss`) + **shadcn/ui** (Radix) components.
- **State**: **Zustand v5** (auth + UI stores, `persist` to localStorage).
- **Server state**: **@tanstack/react-query v5**.
- **HTTP**: **Axios** with request/response interceptors (Bearer auth + token refresh).
- **Forms**: `react-hook-form` + **Zod v4** validation.
- **Charts**: **Recharts v3**. **Animation**: **framer-motion v12**.
- **Testing**: **Jest** + Testing Library (`jest-environment-jsdom`).

### Infrastructure
- **docker-compose** (Postgres 15, Redis 7, backend, frontend).
- **GitHub Actions** CI (`.github/workflows/ci.yml`): backend lint (flake8) +
  black + pytest; frontend `npm ci` + lint + build.

## Folder structure

```
finpilot/
├── CLAUDE.md
├── .claude/                      # this documentation set
├── docker-compose.yml
├── .github/workflows/ci.yml
│
├── backend/
│   ├── main.py                   # FastAPI app: lifespan, middleware, router registration
│   ├── alembic/                  # migrations (env.py + versions/)
│   ├── Dockerfile                # ⚠ COPYs requirements.txt (missing in this repo)
│   ├── .env.example
│   └── app/
│       ├── core/                 # config, database, security, redis, rbac, exceptions, logging, headers
│       ├── api/                  # routers: auth, identity, oauth, market_data, news, portfolio, system
│       │   └── v1/               # ai, analysis, dashboard, documents, integrations, notifications, wealth
│       ├── services/             # auth, identity, oauth, audit (service layer)
│       ├── models/               # SQLAlchemy models (user, rbac, session, portfolio, news, wealth, ...)
│       ├── schemas/              # Pydantic request/response schemas
│       ├── ai/                   # AI gateway, providers, memory, safety, prompt manager, tools
│       ├── agents/               # agent router + specialized agents + agent tools
│       ├── market_data/          # service + adapters (FMP/Finnhub/AlphaVantage/FRED/EDGAR/Mock) + cache
│       ├── document_intelligence/# parser, chunker, embedder, vector_store, retriever, RAG engine
│       ├── analysis/             # ratios, valuation, forecasting, risk, scoring engines
│       ├── portfolio/            # engine, performance, allocation, risk, benchmark, transaction
│       ├── news/                 # engine, providers, sentiment, scoring, impact, summarization
│       ├── wealth/               # budget, cashflow, networth, goals, planning, coach engines
│       ├── dashboard/            # orchestration engine, per-section builders, cache, schemas
│       ├── notifications/        # engine, rules, generators, delivery, queue, worker
│       ├── integrations/         # engine, providers, banks/brokers (mock), import/export, sync, scheduler, audit
│       ├── db/seed.py            # seeds RBAC roles
│       └── worker/               # background worker entry
│
└── frontend/
    ├── app/                      # Next.js App Router
    │   ├── page.tsx              # public landing (⚠ Module-0 placeholder in this repo)
    │   ├── layout.tsx            # root layout + providers
    │   ├── (auth)/               # login, register, forgot/reset-password, verify, 403, account-locked, ...
    │   └── (dashboard)/          # dashboard, portfolio, market, analysis, documents, news, wealth,
    │                             #   ai, notifications, integrations, settings (route group = auth-gated shell)
    ├── features/                 # one folder per module: api/, components/, charts/, tables/, types/, hooks/
    ├── components/               # ui/ (shadcn), layout/ (Sidebar, TopNavigation), auth/, cards/
    ├── services/api.ts           # axios client + interceptors
    ├── store/                    # zustand: auth.ts, ui.ts
    ├── providers/                # QueryProvider, ThemeProvider, RootProviders
    ├── middleware.ts             # edge route gating (cookie-based)
    ├── lib/                      # utils, (sanitize in working copy)
    └── __tests__/                # Jest tests mirroring features/components
```

## Coding standards

- **Module boundaries are load-bearing.** Backend engines are pure business logic;
  API routers are thin and delegate to engines/services. Do not put business logic
  in routers or in the frontend.
- **Frontend is presentation-only.** Each feature's `api/queries.ts` (or `api/index.ts`)
  is the single place that talks to the backend and **maps backend shapes → view
  models**. Components consume hooks, never call `apiClient` directly for domain data.
- **Naming**: backend snake_case (Python) and snake_case JSON fields; frontend
  camelCase. The mapping happens in the frontend `api/` layer.
- **Auth**: every protected backend route depends on `get_current_user`; RBAC via
  `RequiresPermission("perm:name")`. The frontend attaches the Bearer token through
  the axios request interceptor.
- **Errors**: backend raises `FinPilotException`/`HTTPException` → JSON `{error:{code,message}}`.
  Frontend surfaces friendly messages; widgets render `WidgetError`/empty states, not raw errors.
- **Tests**: colocated under `backend/tests/` and `frontend/__tests__/`. Keep them
  green; add coverage with each change. Frontend tests mock `features/*/api/queries`.
- **TypeScript**: `tsc --noEmit` must pass. Prefer typed adapters over `any` in new code.
- **No fabricated data** anywhere in the product surface.

## How the project should be maintained

1. **Start each session** by reading `CLAUDE.md`, `.claude/context.md`, and
   `.claude/current-sprint.md`.
2. **Ground truth is the code.** Before trusting any doc claim, verify against the
   actual files (this matters because of the working-copy divergence — see `CLAUDE.md`).
3. **Fix within boundaries.** Match surrounding patterns; keep routers thin, engines
   pure, frontend presentation-only.
4. **Verify every change**: run the relevant backend/frontend tests, `tsc`, and the
   build. Drive the real UI when a change is user-visible.
5. **Update these docs** — especially `changelog.md`, `current-sprint.md`, and
   `roadmap.md` — as part of finishing any unit of work, so the next session inherits
   accurate context.
