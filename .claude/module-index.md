# Module Index

Per-module map of files, services, hooks, APIs, models, and key deps. Paths are
relative to `backend/` or `frontend/`. ⚠ marks known contract gaps in *this* repo.

---

## Auth & Identity (Module 0 / F1)

- **Purpose**: registration, login, JWT access + rotating refresh tokens, logout,
  session management, password reset, email verify, OAuth (Google), RBAC.
- **Frontend files**: `features/auth/components/{LoginForm,RegisterForm,ForgotPasswordForm,ResetPasswordForm,VerifyEmail,ProfileForm}.tsx`,
  `features/auth/utils/validations.ts` (Zod), `features/auth/types/`,
  `components/auth/{ProtectedRoute,RoleGuard}.tsx`, `store/auth.ts`,
  `services/api.ts` (interceptors), `middleware.ts`, `app/(auth)/*`.
- **Backend files**: `app/api/auth.py`, `app/api/identity.py`, `app/api/oauth.py`,
  `app/api/deps.py`, `app/core/{security,rbac,security_headers}.py`.
- **Services**: `app/services/{auth,identity,oauth,audit}.py`.
- **Hooks**: `features/auth/api/index.ts` (`authApi.{login,register,logout,refresh,getCurrentUser,updateProfile,verifyEmail,forgotPassword,resetPassword}`).
- **APIs**: `/api/v1/auth/{register,login,refresh,logout,sessions}`,
  `/api/v1/users/{me,verify-email,password-reset/*,premium-data}`,
  `/api/v1/oauth/google/{login,callback}`.
- **Models**: `User`, `Role`, `Permission`, `role_permissions`, `DeviceSession`, `AuditLog`.
- **Deps**: passlib[argon2], python-jose, authlib, redis; zustand, axios, react-hook-form, zod.
- ⚠ Working copy: added `user` to auth responses, `useLogout` + account menu, token-type check.

## Dashboard (Module 9 / F2)

- **Purpose**: aggregated overview (KPIs, portfolio snapshot, market, news, AI
  insights, watchlist, calendar, notifications, activity).
- **Frontend**: `features/dashboard/widgets/*.tsx`, `features/dashboard/components/{WidgetGrid,WidgetCard,WidgetSkeleton,WidgetError,WidgetEmpty,DashboardHeader}.tsx`,
  `app/(dashboard)/dashboard/page.tsx`.
- **Backend**: `app/api/v1/dashboard.py`, `app/dashboard/{engine,overview,portfolio,market,news,insights,wealth,watchlist,calendar,cache,schemas}.py`.
- **Hooks**: `features/dashboard/api/queries.ts` (`useDashboardOverview,useKPIs,useMarketOverview,useDashboardNews,useAIInsights`), `api/index.ts` (`dashboardApi`).
- **APIs**: `/api/v1/dashboard/{overview,portfolio,market,news,insights,wealth,watchlist,calendar}` and `/api/v1/dashboard/` (full).
- **Models**: reads from portfolio/wealth/news/notification models via engines.
- **Deps**: recharts, framer-motion; redis (cache).
- ⚠ This repo: 4 widgets hardcode mock data; frontend calls `/dashboard/kpis`,
  `/market/overview`, `/ai/insights`, `/news/dashboard` (don't exist). Working copy
  mapped real sections + empty states.

## Portfolio (Module 8 / F3)

- **Purpose**: portfolios, holdings, transactions, analytics (performance/allocation/risk/benchmark).
- **Frontend**: `features/portfolio/{components,charts,tables,dialogs}/*.tsx`,
  `app/(dashboard)/portfolio/{page.tsx,[ticker]/page.tsx}`.
- **Backend**: `app/api/portfolio.py`, `app/portfolio/{engine,performance,allocation,risk,benchmark,transaction}.py`, `app/schemas/portfolio.py`.
- **Hooks**: `features/portfolio/api/queries.ts`
  (`usePortfolioSummary,usePortfolioHoldings,usePortfolioPerformance,usePortfolioAllocation,usePortfolioTransactions,useBenchmarkMetrics`).
- **APIs**: `/api/v1/portfolios/` (GET/POST), `/{id}`, `/{id}/transactions` (POST), `/{id}/analytics`.
- **Models**: `Portfolio`, `Holding`, `Transaction`.
- **Deps**: MarketDataService (quotes/profiles), AnalysisEngine; recharts, @tanstack/react-table.
- ⚠ Working copy: adapter maps `/portfolios/` + `/{id}/analytics`; added `/{id}/holdings`.

## Market (Module 1 / F4)

- **Purpose**: quotes, company profile, ratios, financials, valuation, earnings,
  indices, search.
- **Frontend**: `features/market/{components,charts,tables}/*.tsx`,
  `app/(dashboard)/market/{page.tsx,[ticker]/page.tsx,search/page.tsx}`.
- **Backend**: `app/api/market_data.py`, `app/market_data/{service,cache,interfaces,models}.py`, `app/market_data/adapters/*` (fmp, finnhub, alphavantage, fred, exchangerate, edgar, mock).
- **Hooks**: `features/market/api/queries.ts`.
- **APIs**: `/api/v1/market-data/{quote,profile,ratios,financials/*,historical,earnings,dividends,splits,sector,indices,news,search,exchange-rate,economic}/{ticker}`.
- **Models**: none persisted (adapter/cache driven).
- **Deps**: httpx, yfinance, tenacity; MockAdapter fallback when API keys absent; redis cache.
- ⚠ Frontend calls `/api/v1/market/*` (backend is `/market-data/*`); breadth/trending/analysts/peers/indicators/valuation/ai-research have **no backend** (see roadmap).

## News (Module 6 / F5)

- **Purpose**: market news, sentiment, entity extraction, portfolio impact, AI summaries.
- **Frontend**: `features/news/{components,charts,timeline}/*.tsx`,
  `app/(dashboard)/news/{page.tsx,article/[id]/page.tsx,company/[ticker]/page.tsx}`.
- **Backend**: `app/api/news.py`, `app/news/{engine,extraction,impact,scoring,sentiment,summarization}.py`, `app/news/providers/*` (alphavantage, finnhub, fmp, newsapi, rss, sec).
- **Hooks**: `features/news/api/queries.ts`.
- **APIs**: `/api/v1/news/{latest,company/{ticker},portfolio/{id},search,ingest}`.
- **Models**: `app/models/news.py`.
- **Deps**: httpx, xml/rss parsing, DOMPurify (sanitize article HTML on the client).
- ⚠ Frontend expects `/news/feed`, `/news/article/{id}`, `/news/entities/{id}`,
  `/news/company/{id}/ai-summary`, `/news/portfolio-impact`; several have no backend.

## Wealth (Module 11 / F6)

- **Purpose**: net worth, cash flow, budgets, financial goals, planning, AI coach.
- **Frontend**: `features/wealth/{components,charts,tables}/*.tsx`,
  `app/(dashboard)/wealth/{page.tsx,accounts,budget,cashflow,planning,transactions}/page.tsx`.
- **Backend**: `app/api/v1/wealth.py`, `app/wealth/{budget,cashflow,networth,goals,planning,coach}.py`, `app/schemas/wealth.py`.
- **Hooks**: `features/wealth/api/queries.ts`
  (`useNetWorthSummary,useNetWorthHistory,useAccounts,useTransactions,useBudgetSummary,useBudgetCategories,useCashFlowSummary,useFinancialGoals,useWealthPlan,useAICoach,useWealthTimeline`).
- **APIs**: `/api/v1/wealth/{accounts,transactions,budgets,goals,analytics/{networth,budget,cashflow,goals,planning},coach/advice}`.
- **Models**: `app/models/wealth.py` (accounts, transactions, budgets, goals).
- **Deps**: AIFinancialCoach → AI Gateway; NewsIntelligenceEngine (macro context); recharts.
- ⚠ Working copy: adapter maps `/wealth/analytics/*` + `/coach/advice`; fixed a
  backend `coach/advice` 500 (bad `AIGatewayService.chat()` kwargs).

## AI Copilot & RAG (Modules 2 & 3 / F7)

- **Purpose**: chat assistant (agent routing + tools) and document RAG.
- **Frontend**: `features/ai/chat/{ChatContainer,ChatInput,MarkdownRenderer,ToolExecutionCard,ChartCard,CitationCard}.tsx`,
  `features/ai/history/HistorySidebar.tsx`, `features/ai/components/PromptCard.tsx`,
  `features/ai/files/FileCard.tsx`, `app/(dashboard)/ai/{page.tsx,chat/[id]/page.tsx}`,
  `app/(dashboard)/documents/page.tsx`.
- **Backend (AI)**: `app/api/v1/ai.py`, `app/ai/{gateway,memory_manager,prompt_manager,safety,metrics,tool_registry,models}.py`, `app/ai/providers/{base,gemini}.py`, `app/agents/{router,base,models,prompts,tools}.py`, `app/agents/specialized/*`.
- **Backend (RAG)**: `app/api/v1/documents.py`, `app/document_intelligence/{parser,chunker,embedder,vector_store,retriever,engine,models}.py`.
- **Hooks**: `features/ai/api/queries.ts` (`useChatHistory,useChatSession,useSuggestedPrompts,useActiveContext,useDeleteSession,useRenameSession,useUploadFile`; working copy adds `useSendChatMessage`).
- **APIs (exist)**: `POST /api/v1/ai/chat`, `POST /api/v1/documents/{upload,query}`.
- **APIs (missing)**: `/ai/{history,session/{id},prompts,context,upload}` — no backend.
- **Models**: AI memory in Redis (not SQL); RAG vector store is in-memory, `user_id`-scoped.
- **Deps**: google-genai (gemini-2.5-flash), tenacity, redis; react-markdown, remark-gfm, react-syntax-highlighter, react-textarea-autosize.
- ⚠ This repo: send path is a mock + hits 404 endpoints. Working copy wired the
  landing/chat inputs and prompt cards to `POST /ai/chat` with friendly error handling.

## Notifications (Module 12 / F8)

- **Purpose**: notification feed, rules/automation, preferences, delivery, background worker.
- **Frontend**: `features/notifications/{components,automation,preferences,rules,timeline}/*.tsx`,
  `app/(dashboard)/notifications/{page.tsx,automation,preferences}/page.tsx`.
- **Backend**: `app/api/v1/notifications.py`, `app/notifications/{engine,rules,generators,delivery,queue,worker}.py`, `app/schemas/notification.py`.
- **Hooks**: `features/notifications/api/queries.ts`
  (`useNotifications,useUnreadCount,useAutomations,usePreferences,useActivityTimeline,useMarkAsRead,useArchiveNotification,useToggleAutomation`).
- **APIs**: `/api/v1/notifications` (list), `/unread`, `/history`, `/rules` (GET/POST),
  `/preferences` (GET/PUT), `/read/{id}`, `/archive/{id}`, `/snooze/{id}`, `/templates`, `/test`.
- **Models**: `Notification`, `NotificationRule`, `NotificationPreference`, `NotificationTemplate`.
- **Deps**: redis queue; background worker started in `main.py` lifespan.
- ⚠ Working copy: mapped `unread-count→/unread`, `automations→/rules`, `timeline→/history`,
  `{id}/read→/read/{id}`, `{id}/archive→/archive/{id}`; fixed a feed crash on empty data.

## Integrations (Module 10 / F9-part)

- **Purpose**: connect banks/brokers, import/export, sync jobs, API keys, audit.
- **Frontend**: `features/settings/pages/IntegrationHub.tsx`, `features/integrations/*` (where present),
  `app/(dashboard)/integrations/page.tsx` (⚠ stub in this repo).
- **Backend**: `app/api/v1/integrations.py`, `app/integrations/{engine,providers,sync,scheduler,import_engine,export_engine,audit,auth}.py`, `app/integrations/{banks,brokers}/mock.py`.
- **APIs**: `/api/v1/integrations/{providers,connect,disconnect/{id},sync/{id},jobs/sync,import,export,audit,health}`.
- **Models**: `app/models/integration.py`.
- ⚠ Frontend calls `/integrations`, `/integrations/keys` (not exposed); `/integrations/*` page is a stub.

## Analysis (Module 4 / F-part)

- **Purpose**: financial analysis engines (ratios, valuation, forecasting, risk, scoring).
- **Frontend**: `app/(dashboard)/analysis/page.tsx` (⚠ stub in this repo).
- **Backend**: `app/api/v1/analysis.py`, `app/analysis/{engine,ratios,valuation,forecasting,risk,scoring,models}.py`.
- **APIs**: `/api/v1/analysis/analysis/{ticker}`.
- **Deps**: MarketDataService.
- ⚠ Frontend page is a one-line stub; not wired.

## Settings & Admin (F10)

- **Purpose**: profile, security center, API keys, appearance, audit logs, admin dashboard, RBAC-gated admin.
- **Frontend**: `features/settings/pages/{ProfileSettings,SecurityCenter,ApiKeys,AuditLogs,IntegrationHub,AdminDashboard}.tsx`,
  `features/settings/components/SettingsSidebar.tsx`, `app/(dashboard)/settings/*`.
- **Backend**: served by auth/identity/integrations/audit routers; admin gated by `RequiresPermission`.
- **APIs**: `/api/v1/users/me`, `/api/v1/integrations/audit`, etc.
- ⚠ Frontend calls `/auth/profile`, `/auth/security`, `/admin/metrics` (not exposed).
