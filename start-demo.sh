#!/usr/bin/env bash
#
# FinPilot local launcher — sets up (if needed) and starts backend + frontend.
# Usage:  ./start-demo.sh          (from the repo root)
# Stop:   Ctrl+C
#
# Prerequisites: Python 3.11, Node 20+, and Redis running
#   (redis-server, or: brew services start redis)
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- Backend setup -----------------------------------------------------------
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  echo "→ Creating backend virtualenv and installing dependencies…"
  python3.11 -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

# A random dev secret is generated if you haven't exported your own.
export SECRET_KEY="${SECRET_KEY:-$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./finpilot.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export ENVIRONMENT="${ENVIRONMENT:-development}"
export BACKEND_CORS_ORIGINS="${BACKEND_CORS_ORIGINS:-http://localhost:3000}"

echo "→ Seeding roles…"
.venv/bin/python -m app.db.seed

echo "→ Starting backend on http://localhost:8000 …"
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# --- Frontend setup ----------------------------------------------------------
cd "$ROOT/frontend"
[ -d node_modules ] || { echo "→ Installing frontend dependencies…"; npm install; }
[ -f .env.local ] || echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

echo "→ Starting frontend on http://localhost:3000 …"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================================================"
echo "  FinPilot is running."
echo "  App:  http://localhost:3000    API:  http://localhost:8000/docs"
echo "  Create an account from the sign-up screen to get started."
echo "======================================================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" INT TERM
wait
