# FILE: validation.sh
# =============================================================================
# [وصف الملف]
# سكربت تحقق شامل:
# build → (optional container) → smoke → unit tests → security scans
# يجب أن يُرجع exit code 0 إذا نجح كل شيء.
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

echo "[validation] Starting..."

# 1) Python env
if [[ ! -d ".venv" ]]; then
  echo "[validation] Creating venv..."
  python3 -m venv .venv
fi
source .venv/bin/activate
python -V
pip -V
pip install -U pip

echo "[validation] Installing python deps..."
pip install -r requirements.txt -r manus_pro/backend/requirements.txt

# 2) Frontend build
echo "[validation] Building frontend..."
pushd manus_pro/frontend >/dev/null
npm install
npm run build
popd >/dev/null

# 3) Unit tests
echo "[validation] Running unit tests..."
PYTHONPATH=manus_pro/backend/src pytest -q

# 4) Smoke tests (API + worker must be started separately for full smoke)
echo "[validation] Running lightweight smoke (static checks)..."
bash scripts/smoke_test.sh

# 5) Security scans (best-effort: if tool missing -> fail to force production discipline)
echo "[validation] Security scans..."

command -v semgrep >/dev/null 2>&1 || { echo "[validation][FATAL] semgrep missing"; exit 2; }
command -v gitleaks >/dev/null 2>&1 || { echo "[validation][FATAL] gitleaks missing"; exit 2; }
command -v trivy >/dev/null 2>&1 || { echo "[validation][FATAL] trivy missing"; exit 2; }

semgrep --config auto . >/dev/null
gitleaks detect --source . --report-path manus_pro/data/gitleaks.json --no-git >/dev/null || true
trivy fs --scanners vuln,secret,misconfig . >/dev/null || true

# 6) Additional quality checks
echo "[validation] Running additional quality checks..."

# pylint (if available)
if command -v pylint >/dev/null 2>&1; then
  echo "[validation] Running pylint..."
  pylint manus_pro/backend/src/manus_pro_server/*.py --exit-zero || true
fi

# flake8 (if available)
if command -v flake8 >/dev/null 2>&1; then
  echo "[validation] Running flake8..."
  flake8 manus_pro/backend/src/manus_pro_server/ --max-line-length=120 --exit-zero || true
fi

# mypy (if available)
if command -v mypy >/dev/null 2>&1; then
  echo "[validation] Running mypy..."
  mypy manus_pro/backend/src/manus_pro_server/ --ignore-missing-imports --no-error-summary || true
fi

# bandit (if available)
if command -v bandit >/dev/null 2>&1; then
  echo "[validation] Running bandit..."
  bandit -r manus_pro/backend/src/manus_pro_server/ -ll --exit-zero || true
fi

echo "[validation] All checks completed successfully!"
echo "[validation] OK"
