# FinPilot AI — Frontend

Next.js 16 (App Router, React 19, TypeScript) frontend for FinPilot AI.
The frontend is **presentation-only**: business logic lives in the backend, and
each feature maps backend responses to view models under `features/<module>/api/`.

See the [root README](../README.md) for full project setup, architecture, and
environment variables.

## Quick start

```bash
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev          # http://localhost:3000
```

Requires the backend running (see the root README).

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start the dev server |
| `npm run build` | Production build |
| `npm start` | Serve the production build |
| `npm test` | Jest test suite |
| `npx tsc --noEmit` | TypeScript typecheck |
| `npm run lint` | ESLint |

## Structure

```
frontend/
├── app/            App Router routes ((auth) and (dashboard) groups)
├── features/       Feature modules (F1–F10): api/, components/, hooks/, types/
├── components/     Shared UI + layout (Sidebar, TopNavigation, ui/)
├── services/       API client (axios + token refresh)
├── store/          Zustand stores (auth, ui)
└── __tests__/      Jest tests
```
