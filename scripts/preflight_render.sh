#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/6] Checking required files and directories..."
required_paths=(
  "run.py"
  "app/__init__.py"
  "app/routes"
  "app/models"
  "app/utils"
  "requirements.txt"
  ".gitignore"
  "README.md"
)

for path in "${required_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "Missing required path: $path"
    exit 1
  fi
done

echo "[2/6] Verifying top-level app export for gunicorn (run:app)..."
python - <<'PY'
from run import app
assert app is not None
print("run:app import OK")
PY

echo "[3/6] Validating /api/health endpoint..."
python - <<'PY'
from run import app

with app.test_client() as client:
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    payload = response.get_json(silent=True) or {}
    assert payload.get("status") == "ok", payload
    assert payload.get("service") == "health-assist-backend", payload
    assert "env" in payload, payload
print("/api/health OK")
PY

echo "[4/6] Running Python syntax/compile checks..."
python -m compileall -q app run.py

echo "[5/6] Running backend tests..."
pytest -q

echo "[6/6] Preflight checks passed. Backend is deployment-ready."
