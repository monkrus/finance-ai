# Architecture

> Describes the intended architecture of FinPilot AI. Where this repo diverges
> from the stabilized working copy, it is flagged with ⚠.

## High-level shape

```
┌──────────────────────────── Frontend (Next.js 16, React 19) ────────────────────────────┐
│  app/ (App Router)         features/<module>/            store/ (zustand)   services/api.ts │
│   (auth) + (dashboard)  →   components + api/queries  →   auth + ui state  →  axios client   │
│                                     │ (react-query hooks)                         │          │
└─────────────────────────────────────┼──────────────────────────────────────────┼──────────┘
                                       │  HTTP + Bearer JWT  (CORS)                │
┌──────────────────────────────────────▼───────────────────────────────────────────▼─────────┐
│  Backend (FastAPI)   main.py → routers (app/api, app/api/v1)                                  │
│      Router (thin)  →  Service layer (auth/identity/oauth/audit)  →  Domain Engines           │
│                                          │                                                     │
│         AI Gateway ── Gemini    Market Data Service ── adapters    RAG Engine ── vector store  │
│                                          │                                                     │
│   SQLAlchemy async ORM ──► Postgres/SQLite        Redis ──► rate-limit / brute-force / AI mem  │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

Principles: **thin routers → services/engines → data**. Engines are framework-free
business logic. The frontend is a **presentation layer** that maps backend shapes
to view models in each feature's `api/` folder.

---

## Frontend flow

1. **Entry** — `app/layout.tsx` wraps everything in `RootProviders`
   (`ThemeProvider` → `QueryProvider`). `app/page.tsx` is the public landing.
   ⚠ In this repo `page.tsx` is still the Module-0 placeholder ("Foundation Module 0
   active…"); the working copy replaced it with a real marketing landing linking to
   `/login` and `/register`.
2. **Route groups** —
   - `app/(auth)/*` → `/login`, `/register`, `/forgot-password`, `/reset-password`,
     `/verify`, `/403`, `/account-locked`, `/session-expired`. Parentheses strip the
     group name from the URL.
   - `app/(dashboard)/*` → the authenticated shell (`(dashboard)/layout.tsx` renders
     `Sidebar` + `TopNavigation` inside `ProtectedRoute`). Sub-routes: `dashboard`,
     `portfolio[/ticker]`, `market[/ticker|/search]`, `analysis`, `documents`,
     `news[/article/id|/company/ticker]`, `wealth[/accounts|/budget|/cashflow|/planning|/transactions]`,
     `ai[/chat/id]`, `notifications[/automation|/preferences]`, `integrations`,
     `settings[/profile|/security|/admin|/api-keys|/appearance|/audit|/integrations|/notifications|/privacy]`.
     (42 `page.tsx` total.)
3. **Data fetching** — components call hooks from `features/<module>/api/queries.ts`.
   Each hook uses `@tanstack/react-query` and, in its `queryFn`, calls
   `apiClient` (`services/api.ts`) then maps the snake_case backend payload to the
   camelCase view model declared in `features/<module>/types/`.
4. **Loading / empty / error** — widgets render skeletons while `isLoading`,
   empty states when there is no data, and `WidgetError` on `isError`.
5. **Client state** — `store/auth.ts` (user, tokens, `isAuthenticated`, persisted to
   localStorage) and `store/ui.ts` (sidebar, counters).

## Backend flow

1. **Startup** (`main.py` lifespan): init `fastapi-limiter` with Redis, start the
   notifications background worker, and `Base.metadata.create_all` (dev convenience;
   Alembic is the production path).
2. **Middleware** (outer→inner): `SecurityHeadersMiddleware` (HSTS, CSP, X-Frame,
   nosniff, referrer, permissions), `SessionMiddleware` (OAuth), `CORSMiddleware`.
3. **Request** → router (`app/api/*`, `app/api/v1/*`). Routers depend on
   `get_current_user` (auth), `get_db` (async session), and optional
   `RequiresPermission(...)` (RBAC).
4. **Router → Service/Engine**: routers stay thin and delegate. Services
   (`app/services/`) handle auth/identity/oauth/audit; domain **engines**
   (`app/<module>/*.py`) compute results (portfolio analytics, wealth metrics,
   news scoring, dashboard sections, etc.).
5. **Data**: SQLAlchemy async sessions (`AsyncSessionLocal`) → Postgres/SQLite.
   Redis for rate limits, brute-force counters, and AI memory.
6. **Errors**: `FinPilotException` / generic `Exception` handlers return
   `{"error": {"code", "message"}}`; unhandled errors are logged and return 500
   without leaking internals.

## API flow / contract

- **Base path**: `settings.API_V1_STR` = `/api/v1`. Registered prefixes:

  | Tag | Prefix |
  |---|---|
  | auth | `/api/v1/auth` |
  | users (identity) | `/api/v1/users` |
  | oauth (Google) | `/api/v1/oauth/google` |
  | market-data | `/api/v1/market-data` |
  | ai | `/api/v1/ai` |
  | documents | `/api/v1/documents` |
  | analysis | `/api/v1/analysis` |
  | portfolio | `/api/v1/portfolios` |
  | news | `/api/v1/news` |
  | wealth | `/api/v1/wealth` |
  | dashboard | `/api/v1` (sections under `/dashboard/*`) |
  | notifications | `/api/v1/notifications` |
  | integrations | `/api/v1/integrations` |
  | system | `/` (`/health`, `/`) |

- **Contract mapping**: backend returns snake_case; the frontend `features/*/api/`
  layer adapts to camelCase view models. Several frontend modules were written
  against endpoint names that differ from what the backend exposes; the working
  copy reconciled Portfolio, Wealth, Notifications, Dashboard, and AI (see
  `changelog.md`). Market, News detail, and some AI sub-features remain unmapped.
- **Auth**: `Authorization: Bearer <access JWT>` on every protected call; the axios
  request interceptor injects it, the response interceptor refreshes on 401.

## Database structure

SQLAlchemy async models (`backend/app/models/`), owned per module:

- **user.py** — `User` (email, hashed_password nullable for OAuth, is_active,
  is_verified, avatar_url, role_id, timestamps). Relationships: `role` (selectin),
  `portfolios`, `sessions`, `audit_logs` (cascade delete).
- **rbac.py** — `Role`, `Permission`, `role_permissions` (M2M). Role→permissions
  selectin-loaded.
- **session.py** — `DeviceSession` (refresh_token, ip, user_agent, is_revoked,
  expires_at) — server-side refresh-token store enabling rotation & revocation.
- **portfolio.py** — `Portfolio` (user_id owner, name, currency, is_public),
  `Holding` (ticker, asset_type, quantity, average_buy_price, cost_basis,
  realized_gain_loss), `Transaction` (type BUY/SELL/DIVIDEND/DEPOSIT/…, quantity,
  price_per_unit, fees, taxes, total_amount). Cascade: portfolio→holdings→transactions.
- **wealth.py** — accounts, transactions, budgets, goals (wealth module persistence).
- **news.py** — news articles / entities / impact persistence.
- **notification.py** — `Notification`, `NotificationRule`, `NotificationPreference`,
  `NotificationTemplate`.
- **integration.py** — external account connections, sync jobs, API keys/audit.
- **audit.py** — `AuditLog` (action, status, user_id, ip) for security events.

Migrations: `backend/alembic/versions/` (initial identity migration present; dev
relies on `create_all`, prod should use Alembic).

## Authentication flow

**Design**: short-lived JWT **access token** (15 min) + long-lived **opaque refresh
token** (7 days) with **rotation** and server-side **revocation**.

1. **Register/Login** (`app/api/auth.py` → `AuthService`):
   - Password hashed with **Argon2**; brute-force lockout keyed on `email+ip` in Redis
     (5 attempts / 5 min → 429).
   - On success: mint access JWT (`create_access_token`, HS256, `type:"access"`),
     create a `DeviceSession` with an opaque `secrets.token_urlsafe` refresh token.
   - Response: `{access_token, token_type, refresh_token, user}` (⚠ the `user` field
     and camelCase user payload were added in the working copy; original RC1 returned
     no `user`).
2. **Authorization** (`app/api/deps.py::get_current_user`): decode JWT, verify
   `type=="access"` (working copy), load `User`; inactive → 400.
3. **Refresh** (`/auth/refresh`): look up `DeviceSession` by refresh token; if valid
   and not revoked/expired → mint new access token, **rotate** (new session, revoke old).
4. **Logout** (`/auth/logout`): revoke the `DeviceSession` by refresh token.
   ⚠ In this repo no UI calls it; the working copy added a `useLogout` hook + account menu.
5. **Frontend**: `services/api.ts` request interceptor adds the Bearer token; the
   response interceptor transparently refreshes on 401 and retries (with a queue);
   `store/auth.ts` persists `{user, accessToken, refreshToken, isAuthenticated}`.
   `middleware.ts` performs coarse cookie-based route gating; `ProtectedRoute`
   enforces client-side. **RBAC**: `RequiresPermission` on the backend, `RoleGuard`
   on the frontend.

## AI flow (Copilot + RAG)

- **AI Gateway** (`app/ai/gateway.py`, `AIGatewayService`) orchestrates a turn:
  `SafetyFilter.validate_input` → `MemoryManager` (sliding-window history in Redis,
  keyed by session id, 24 h TTL) → `PromptManager.render(system_prompt)` →
  `GeminiProvider.generate_content` → tool calls via `ToolRegistry` (parallel) →
  re-prompt → `validate_output` → `MetricsTracker`. Exceptions degrade gracefully
  to an `error_recovery` fallback string (no crash/hang).
- **Provider** (`app/ai/providers/gemini.py`): `google-genai`, model
  `gemini-2.5-flash`, `tenacity` retries + 30 s timeout. If `GEMINI_API_KEY` is
  unset, a dummy key is used and calls return the graceful fallback.
- **Agent routing** (`app/agents/router.py`): zero-shot intent classification →
  one of FINANCIAL_ADVISOR, STOCK_RESEARCH, NEWS_ANALYSIS, PORTFOLIO_ADVISOR,
  FINANCE_TUTOR, RESEARCH_ASSISTANT.
- **Endpoint** (`app/api/v1/ai.py`): `POST /api/v1/ai/chat {session_id, message,
  stream}` → `{response}` (or SSE when `stream:true`). The session id is namespaced
  by user (`user:{id}:{session_id}`) so memory can never cross tenants.
- **RAG** (`app/document_intelligence/`, `app/api/v1/documents.py`): upload →
  `DocumentParser` → `FinancialChunker` → `GeminiEmbedder` → `InMemoryVectorStore`
  (scoped by `user_id`) → `HybridRetriever` (semantic + keyword RRF) → `RAGEngine`
  grounded generation with citations. `POST /documents/upload`, `POST /documents/query`.
- **Frontend**: `features/ai/` (chat container, input, history sidebar, markdown
  renderer, tool/chart/citation cards). ⚠ In this repo the send path is a mock and
  calls non-existent endpoints; the working copy wired it to `POST /ai/chat`.

## Market module

- **Backend**: `app/market_data/` — `MarketDataService` fans out to adapters
  (FMP, Finnhub, AlphaVantage, FRED, ExchangeRate, EDGAR) with **graceful
  degradation to `MockAdapter`** when keys are missing; `cache.py` (Redis) memoizes.
  Router `app/api/market_data.py` at `/api/v1/market-data/*` (quote, profile, ratios,
  financials, historical, earnings, dividends, splits, sector, indices, news, search,
  exchange-rate, economic).
- **Frontend**: `features/market/` (charts: PriceChart; components: CompanyProfile,
  FinancialRatios, ValuationModels, AnalystRatings, EarningsTimeline, GlobalMarkets,
  MarketHeatmap, TechIndicators, AIResearchReport; tables: FinancialStatementsTable,
  PeerComparison). ⚠ Frontend calls `/api/v1/market/*` which the backend does **not**
  expose (backend is `/market-data/*`); several sub-features (breadth, trending,
  analysts, peers, indicators, valuation, ai-research) have **no backend** — see
  `roadmap.md` / `changelog.md`.

## News module

- **Backend**: `app/news/` — `NewsIntelligenceEngine` with providers (AlphaVantage,
  Finnhub, FMP, NewsAPI, RSS, SEC), plus sentiment, scoring, entity extraction,
  portfolio impact, summarization. Router `app/api/news.py` at `/api/v1/news/*`
  (latest, company/{ticker}, portfolio/{id}, search, ingest).
- **Frontend**: `features/news/` (NewsFeed, AISummaryBox, PortfolioImpact,
  SentimentTrend, EntityVisualization, EventTimeline). ⚠ Frontend calls
  `/news/feed`, `/news/article/{id}`, `/news/entities/{id}`,
  `/news/company/{id}/ai-summary`, `/news/portfolio-impact` — backend exposes
  `/news/latest` etc.; article-detail/entities/ai-summary have no backend.

## Portfolio module

- **Backend**: `app/portfolio/` — `PortfolioEngine` composes `PerformanceEngine`,
  `AllocationEngine`, `PortfolioRiskEngine`, `BenchmarkEngine`; `TransactionEngine`
  applies BUY/SELL/etc. and maintains holdings/cost basis. Router
  `app/api/portfolio.py` at `/api/v1/portfolios/*`: `GET/POST /`, `GET /{id}`,
  `POST /{id}/transactions`, `GET /{id}/analytics` (holdings are hydrated with live
  market data → performance/allocation/risk).
- **Frontend**: `features/portfolio/` (OverviewCards, HoldingsTable, TransactionDialog,
  charts: PortfolioGrowthChart, AllocationDoughnut, RiskHeatmap; PortfolioHero,
  PortfolioAIInsights, PortfolioNews). ⚠ Frontend originally called
  `/portfolio/{summary,holdings,allocation,performance,transactions}` (singular,
  non-existent); the working copy mapped these onto `/portfolios/` + `/{id}/analytics`
  and added a hydrated `/{id}/holdings` route.

## Wealth module

- **Backend**: `app/wealth/` — engines for budget, cashflow, networth, goals,
  planning, plus `AIFinancialCoach` (gathers financial context + macro news → AI
  gateway). Router `app/api/v1/wealth.py` at `/api/v1/wealth/*`: accounts,
  transactions, budgets, goals, `analytics/{networth,budget,cashflow,goals,planning}`,
  `coach/advice`.
- **Frontend**: `features/wealth/` (NetWorthChart, CashFlowSankey, RetirementGauge,
  BudgetDashboard, GoalsTracker, AccountsTable, TransactionsTable, AICoachCard,
  WealthTimeline). ⚠ Frontend originally called `/wealth/{networth/summary,
  budget/summary,cashflow,plan,coach,timeline}`; the working copy mapped these onto
  `/wealth/analytics/*` and `/wealth/coach/advice`, and fixed a backend
  `coach/advice` 500 (wrong `AIGatewayService.chat()` kwargs).

## Dashboard module

- **Backend**: `app/dashboard/` — `DashboardEngine` orchestrates per-section builders
  (overview, portfolio, market, news, insights, wealth, watchlist, calendar) into a
  generic `{widgets: [WidgetSchema]}` envelope; `cache.py` (Redis) memoizes. Router
  `app/api/v1/dashboard.py` at `/api/v1/dashboard/*`.
- **Frontend**: `features/dashboard/` (WidgetGrid, KPIWidget, PortfolioSnapshotWidget,
  MarketOverviewWidget, NewsWidget, AIInsightsWidget, WatchlistWidget, CalendarWidget,
  NotificationWidget, RecentActivityWidget). ⚠ In this repo four widgets render
  **hardcoded mock financial data** and the frontend calls a few non-existent
  endpoints; the working copy wired the real `/dashboard/*` sections and replaced all
  fabricated data with empty states.
