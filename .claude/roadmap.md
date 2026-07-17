# Roadmap

_Last updated: 2026-07-18._

Legend: ✅ done · 🚧 in progress · 📋 planned · ⚠ done in working copy, **not merged
into this repo**.

---

## Version 1 — Completed

The **v1.0 RC1 "feature-complete" build** present in this repository:

- ✅ **Backend Modules 0–12 implemented** as framework-free engines behind thin
  routers: identity/auth + RBAC, market data (multi-provider + mock fallback),
  AI gateway + agents, document RAG, analysis, portfolio, news intelligence,
  wealth, dashboard orchestration, notifications (+ worker), integrations.
- ✅ **Frontend Modules F1–F10 UI**: auth flows, dashboard, portfolio, market,
  news, wealth, AI copilot, notifications, settings/admin — built with Next.js 16
  App Router, shadcn/ui, Zustand, react-query, Recharts.
- ✅ **Auth system**: Argon2 hashing, JWT access + rotating opaque refresh tokens,
  brute-force lockout, RBAC, Google OAuth scaffolding, device sessions.
- ✅ **AI + RAG engines**: Gemini gateway with safety filter, sliding-window memory,
  prompt manager, tool registry; hybrid-retrieval RAG with citations.
- ✅ **Backend test suite** (~60 files) and **frontend Jest suite**.
- ✅ **Infra**: docker-compose (Postgres/Redis), GitHub Actions CI definition.

## Version 1 — In Progress (stabilization toward shippable v1.0)

Work identified by the RC1 audit + UAT. Items marked ⚠ are **completed in the
active working copy but not merged into this repository** (see `changelog.md`).

### Build / run blockers
- ⚠ Reconstructed `backend/requirements.txt` (Docker + CI depend on it).
- ⚠ Added `frontend/postcss.config.mjs` (Tailwind v4 otherwise doesn't compile).
- ⚠ Added missing frontend deps (`date-fns`, `react-markdown`, `remark-gfm`,
  `react-syntax-highlighter`, `react-textarea-autosize`, `@radix-ui/react-switch`,
  `dompurify`) and two missing shadcn components (`switch`, `textarea`).
- ⚠ `docker-compose` backend `SECRET_KEY`; CI `pytest-benchmark`.
- 🚧 Merge the working copy's stabilization commits into this repository.

### Correctness / security (RC1 audit)
- ⚠ Frontend↔backend **auth contract** aligned (login/register return `user`;
  refresh/logout send the refresh token; middleware session cookie; token-type check).
- ⚠ **RAG multi-tenancy**: retrieval scoped by `user_id`.
- ⚠ **AI chat memory isolation**: session ids namespaced per user.
- ⚠ **News XSS**: article HTML sanitized with DOMPurify.
- ⚠ **Password policy** enforced server-side; deps `int()`/500 guard.

### Stabilization sprints
- ⚠ **P0-1 Logout** — `useLogout` hook + account menu; server session revoke; cache clear.
- ⚠ **P0-2 De-fabricated dashboard** — removed hardcoded holdings/trades/watchlist/
  events/notifications; empty states for new users.
- ⚠ **P0-3 AI Copilot restored** — wired send to `POST /ai/chat`; friendly
  unavailable/error handling.
- ⚠ **Module wiring**: Portfolio, Wealth, Notifications, Dashboard mapped to real endpoints.

### Still open (not done anywhere yet)
- 📋 **Register form validation display** — schema blocks submit but renders no errors.
- 📋 **Mobile responsiveness** — sidebar does not collapse; content clipped < 768px.
- 📋 **Market module wiring** — map `/market-data/*` to the market UI; ~8 sub-features
  (breadth, trending, analysts, peers, indicators, valuation, ai-research) have no backend.
- 📋 **News detail wiring** — `/news/latest` mapping; article-detail/entities/ai-summary
  endpoints missing.
- 📋 **Stub pages** — `analysis`, `documents`, `integrations` are one-line placeholders.
- 📋 **Missing backend endpoints** — AI history/sessions/prompts/upload, admin metrics,
  integrations list/keys, auth profile/security.
- 📋 **Email verification** enforcement; refresh-token hashing at rest; token in
  localStorage (XSS surface); nullable boolean columns + migration-only schema.
- 📋 **Greeting personalization** (backend `User` has no name fields).

## Version 2 — Planned

- 📋 **Live AI streaming** consumed on the frontend (backend already supports SSE).
- 📋 **Persistent AI conversation history** (new backend endpoints + storage).
- 📋 **Real market/news data** in production (provider keys; replace mock fallback;
  build the missing analytics endpoints).
- 📋 **Persistent, shared RAG vector store** (replace in-memory; multi-worker/replica).
- 📋 **Real integrations** (bank/broker aggregation beyond mock adapters).
- 📋 **Analysis workspace** (wire the analysis engines into a real UI).
- 📋 **Observability & scale**: multi-worker backend, migration-first schema,
  rate-limit tuning, metrics/telemetry.
- 📋 **Accessibility & responsive** pass across all pages; dark/light theming polish.
- 📋 **Notifications delivery** channels (email/push) beyond in-app.
