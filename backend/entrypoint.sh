#!/usr/bin/env bash
set -euo pipefail

# Apply migrations before the app starts (PRD §16: migrations run on deploy).
echo "Running database migrations..."
alembic upgrade head

echo "Starting NetDocs API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
