#!/usr/bin/env bash
set -euo pipefail

# Basic env checks
if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Aborting." >&2
  exit 1
fi

echo "STEP 1: Creating DB..."
python -m app.db.create_db

echo "STEP 1.5: Testing DB connectivity..."
python - <<'PY'
import os, sys
from sqlalchemy import create_engine, text
try:
    eng = create_engine(os.environ["DATABASE_URL"], connect_args={"connect_timeout": 5})
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("DB connectivity OK")
except Exception as e:
    print("DB connectivity FAILED:", e, file=sys.stderr)
    sys.exit(2)
PY

echo "STEP 2: Ingesting weather data..."
DATA_DIR=${WX_DATA_DIR:-/data/wx_data}
if [ -d "$DATA_DIR" ]; then
  echo "Using data dir: $DATA_DIR"
  WX_DATA_DIR_ARG="--data-dir $DATA_DIR"
else
  WX_DATA_DIR_ARG=""
fi

# If S3 is expected, require creds
if [ -n "${S3_BUCKET:-}" ] || [ -n "${S3_KEY:-}" ]; then
  if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
    echo "ERROR: S3_BUCKET/S3_KEY set but AWS credentials missing. Aborting." >&2
    exit 1
  fi
  echo "S3 config detected: bucket=${S3_BUCKET:-<not set>}"
fi

python -m app.ingest $WX_DATA_DIR_ARG

echo "STEP 3: Computing yearly stats..."
python -m app.analysis

echo "ALL DONE! Starting web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload