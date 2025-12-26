#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
echo "Root dir: $ROOT_DIR"

# 1) Prepare Python environment for backend
cd "$ROOT_DIR/manus_pro/backend"
if [ -f "requirements.txt" ]; then
  if [ ! -d ".venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv .venv || python -m venv .venv
  fi
  source .venv/bin/activate
  echo "Installing backend requirements..."
  pip install --upgrade pip setuptools wheel
  pip install -r requirements.txt || true
fi

# 2) Build frontend (if node available)
if [ -d "$ROOT_DIR/manus_pro/frontend" ]; then
  echo "Building frontend..."
  cd "$ROOT_DIR/manus_pro/frontend"

  if command -v npm >/dev/null 2>&1; then
    if [ ! -d "node_modules" ]; then
      echo "Installing frontend dependencies (npm ci)..."
      npm ci || npm install || true
    fi
    npm run build --if-present
  else
    echo "npm not found; skipping frontend build. Ensure frontend/dist exists or install Node.js."
  fi
fi

# 3) Start worker (if exists) in background
cd "$ROOT_DIR/manus_pro/backend"
if python -c "import importlib, sys; importlib.import_module('manus_pro_server.worker')" >/dev/null 2>&1; then
  echo "Starting worker in background..."
  python -m manus_pro_server.worker &
  WORKER_PID=$!
else
  echo "No worker module found or failed to import; skipping worker."
  WORKER_PID=
fi

# 4) Start backend (foreground)
echo "Starting backend..."
# Run backend; this entrypoint uses uvicorn inside __main__.py
python -m manus_pro_server &
BACK_PID=$!

# Trap to kill background processes on exit
trap 'echo "Shutting down..."; if [ -n "${WORKER_PID:-}" ]; then kill ${WORKER_PID} || true; fi; kill ${BACK_PID} || true; wait' EXIT INT TERM

# Wait for backend process
wait ${BACK_PID}
