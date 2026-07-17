# Current Sprint

_Updated: 2026-07-18._

## Active task

**Self-documentation / handoff.** Create `CLAUDE.md` + `.claude/*` so future
sessions can continue without chat history. (This file set.)

## Top open item — reconcile working copy ↔ this repo

The stabilization work (RC1 audit fixes + Sprints P0-1/2/3) was done in a **separate
working copy** and is **not in this repository** (`/Users/prakashk/~:Development/finpilot`).
Before further feature work, decide and act on:

1. **Merge** the working-copy changes into this repo (preferred — otherwise this repo
   won't build: no `requirements.txt`, no `postcss.config`, unstyled UI), **or**
2. Treat this repo as canonical and **re-apply** the fixes here.

Until reconciled, **trust the code over the docs** and re-verify each claim.

## Next queued (post-reconciliation), in priority order

- **P0-4 Register validation display** — schema blocks submit but shows no errors
  (`features/auth/components/RegisterForm.tsx` + `utils/validations.ts`).
- **P0-5 Mobile responsiveness** — sidebar doesn't collapse; content clipped < 768px
  (`components/layout/Sidebar.tsx`, `(dashboard)/layout.tsx`).
- **P1 Market module wiring** — map the market UI onto `/api/v1/market-data/*`; report
  the ~8 sub-features that have no backend.
- **P1 News wiring** — map onto `/api/v1/news/latest`; flag missing article-detail/
  entities/ai-summary endpoints.
- **P2 Stub pages** — `analysis`, `documents`, `integrations` are one-line placeholders.

## Definition of done (every task)

Relevant backend + frontend tests pass · `tsc --noEmit` clean · `npm run build`
green · user-visible changes verified by driving the real UI · `changelog.md` and
this file updated.
