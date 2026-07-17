# Changelog

Reverse-chronological. **Two sections**: what is actually present in *this*
repository, and what was completed in the active working copy but **not yet merged
here**. Verify against code before relying on any entry (see `CLAUDE.md`).

---

## Present in this repository

### v1.0 RC1 — Feature-complete build (baseline)
The repository contains the full RC1 build as originally delivered:

- **Backend (Modules 0–12)** — FastAPI app with:
  - Identity/auth: register, login, JWT access + rotating refresh tokens, device
    sessions, password reset, email-verify scaffolding, Google OAuth scaffolding,
    RBAC (`Role`/`Permission`), Argon2 hashing, Redis brute-force lockout.
  - AI gateway (Gemini `gemini-2.5-flash`) with safety filter, sliding-window Redis
    memory, prompt manager, tool registry, metrics; agent router + 6 specialized agents.
  - Document RAG: parser → financial chunker → Gemini embedder → in-memory vector
    store → hybrid retriever (RRF) → grounded generation with citations.
  - Market data service with FMP/Finnhub/AlphaVantage/FRED/ExchangeRate/EDGAR
    adapters + Mock fallback + Redis cache.
  - Engines: analysis (ratios/valuation/forecasting/risk/scoring), portfolio
    (performance/allocation/risk/benchmark/transaction), news (sentiment/scoring/
    impact/summarization/extraction), wealth (budget/cashflow/networth/goals/planning/coach),
    dashboard orchestration, notifications (rules/generators/delivery/queue/worker),
    integrations (banks/brokers mock, import/export, sync, scheduler, audit).
  - `main.py`: lifespan (rate limiter init, worker start, `create_all`), security
    headers, session + CORS middleware; ~60 pytest files; Alembic initial migration.
- **Frontend (Modules F1–F10)** — Next.js 16 App Router (42 pages), React 19, TS,
  Tailwind v4 + shadcn/ui, Zustand + react-query + axios, Recharts + framer-motion;
  auth flows, dashboard, portfolio, market, news, wealth, AI copilot, notifications,
  settings/admin; Jest test suite.
- **Infra** — docker-compose (Postgres 15, Redis 7), GitHub Actions CI.

**Known issues present in this repo** (unfixed here; fixed in working copy — see below):
`backend/requirements.txt` missing (breaks Docker/CI); `frontend/postcss.config.*`
missing (Tailwind doesn't compile → unstyled UI); root `app/page.tsx` is a Module-0
placeholder with no links; four dashboard widgets render hardcoded fake financial
data; no logout UI; AI Copilot send is a mock hitting non-existent endpoints; many
frontend modules call endpoints the backend doesn't expose.

---

## Completed in working copy (NOT merged here)

> Performed on a separate working copy (the running local dev environment) around
> 2026-07-17. Backend suite ended at **209 passing**, frontend at **100 passing**,
> `tsc` clean, `npm run build` green. These changes are **absent from this repo**.

### RC1 Audit remediation
- **Build**: reconstructed `backend/requirements.txt`; added `frontend/postcss.config.mjs`;
  added missing frontend deps (`date-fns`, `react-markdown`, `remark-gfm`,
  `react-syntax-highlighter`, `react-textarea-autosize`, `@radix-ui/react-switch`,
  `dompurify`) + shadcn `switch.tsx`/`textarea.tsx`; `docker-compose` `SECRET_KEY`;
  CI `pytest-benchmark`; fixed several pre-existing TS errors (React UMD imports,
  Recharts formatter, `NewsItem.headline`→`title`) and an RSC-boundary bug (`'use
  client'` on `PromptCard`).
- **Security/correctness**: aligned the frontend↔backend **auth contract** (login/
  register now return a `user`; refresh & logout send the stored refresh token;
  middleware mirrors a `finpilot_session` cookie; `deps.py` verifies `type=="access"`
  and guards non-numeric `sub`); **RAG retrieval scoped by `user_id`**; **AI chat
  memory namespaced per user** (`user:{id}:{session_id}`); **news article HTML
  sanitized** (DOMPurify) against XSS; **server-side password policy**; env-driven
  CORS; non-root Dockerfile + healthcheck; dashboard Redis cache datetime-serialization fix.
- **Landing page**: replaced the Module-0 placeholder with a real landing linking to
  `/login`/`/register`; defined missing global CSS utilities (`animate-fade-in`,
  `gradient-text`, `glass-panel`, `custom-scrollbar`, `@keyframes`).

### Runtime integration (local end-to-end)
- Installed/started Redis; ran backend on SQLite; seeded RBAC roles; created demo
  data via the real APIs (portfolio + transactions). Fixed a startup crash
  (`fastapi_limiter.init` → `FastAPILimiter.init`).
- **Dashboard** wired to real `/dashboard/*` sections (was calling 4 non-existent
  endpoints); fixed `$NaN`.
- **Portfolio** wired: adapter mapping onto `/portfolios/` + `/{id}/analytics`; added
  a hydrated `GET /portfolios/{id}/holdings` route (engine `_hydrate` refactor);
  fixed a loading-state flash and a diversification-score overflow.
- **Wealth** wired onto `/wealth/analytics/*` + `/coach/advice`; fixed a backend
  `coach/advice` **500** (wrong `AIGatewayService.chat()` kwargs / `model="gpt-4"`).
- **Notifications** remapped (`unread-count→/unread`, `automations→/rules`,
  `timeline→/history`, `{id}/read→/read/{id}`, `{id}/archive→/archive/{id}`); fixed a
  feed crash on empty data.

### Sprint P0-1 — Logout
- Added `features/auth/hooks/useLogout.ts`; turned the dead "User Profile" button into
  an accessible account menu with **Log out**. Revokes the backend session
  (`POST /auth/logout`), clears auth state + `finpilot_session` cookie + React Query
  cache, `router.replace('/login')`. Verified: revoked refresh token → 401, Back can't
  reopen authed pages, refresh stays logged out, repeated login/logout cycles. +4 tests.

### Sprint P0-2 — Eliminate fabricated dashboard data
- Removed all hardcoded financial data from `WatchlistWidget`, `RecentActivityWidget`,
  `CalendarWidget`, `NotificationWidget` (→ empty states) and `PortfolioSnapshotWidget`
  (removed mock allocation + `['AAPL','MSFT','NVDA']`; kept real value; empty/pointer
  states). New users see "You don't have any investments yet.", "No activity yet.",
  etc. +2 tests incl. a fabrication guard.

### Sprint P0-3 — Restore AI Copilot
- Added `useSendChatMessage` (`POST /api/v1/ai/chat`); replaced the mock `handleSend`
  in `ChatContainer` with a real backend call; friendly "temporarily unavailable"
  mapping for the provider-unavailable fallback and a generic error path; wired the
  landing input + suggested prompts to start a chat carrying the first message (`?q=`);
  stopped `useChatSession`/`useChatHistory` from hitting non-existent 404 endpoints;
  fixed a conversation-wipe bug. +8 tests. Verified end-to-end in the browser.

---

## How to keep this changelog

Append a dated entry per unit of work with: what changed, why, files touched, and
verification (tests/tsc/build/manual). When the working-copy changes are merged into
this repo, move the relevant entries into the "Present in this repository" section.
