#!/bin/bash

set -e  # exit on first failure

echo "STEP 1: Creating DB..."
python -m app.db.create_db

echo "STEP 2: Ingesting weather data..."
python -m app.ingest

echo "STEP 3: Computing yearly stats..."
python -m app.analysis

echo "ALL DONE!"
