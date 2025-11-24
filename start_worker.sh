#!/usr/bin/env bash
set -euo pipefail

echo "STEP 1: Creating DB..."
python -m app.db.create_db

echo "STEP 2: Ingesting weather data..."
DATA_DIR=${WX_DATA_DIR:-/data/wx_data}
if [ -d "$DATA_DIR" ]; then
  echo "Using data dir: $DATA_DIR"
  WX_DATA_DIR_ARG="--data-dir $DATA_DIR"
else
  WX_DATA_DIR_ARG=""
fi

python -m app.ingest $WX_DATA_DIR_ARG

echo "STEP 3: Computing yearly stats..."
python -m app.analysis

echo "ALL DONE! Starting web server..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
