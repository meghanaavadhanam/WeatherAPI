// ...existing code...
# 🌦️ Weather Station Data API

Small API service that ingests weather data from S3, stores it in PostgreSQL, computes statistics, and exposes endpoints for raw and aggregated data.

---

## Prerequisites

- Docker & Docker Compose
- A copy of .env with DB and AWS credentials:
  - cp .env.example .env
  - Edit values as needed (POSTGRES password, DATABASE_URL, AWS creds if using S3)

Note: This repo assumes you run commands from the root directory.

---

## Quick Start

1. Build and start services
   - Start everything:
     ```
     docker compose up --build -d
     ```

2. Open the API docs
   - http://localhost:8000/docs

3. Run tests
   - From root:
     ```
     make test
     ```
   - (Direct command if not using make)
     ```
     docker compose run --rm -e PYTHONPATH=/code app pytest tests/
     ```

---

## Files & Purpose

Top-level files
- Dockerfile — container image for the app (Python dependencies, working dir /code, runs uvicorn).
- docker-compose.yml — service definitions for app and postgres.
- Makefile — convenience commands (test, lint, format).
- requirements.txt — Python dependencies.
- start_worker.sh — helper script (if present) for background workers or periodic tasks.
- readme.md — this file.
- tests/ — pytest unit tests (example: test_models.py).

app/ (application package)
- __init__.py — package marker and any top-level initializations.
- main.py — FastAPI app factory and route mounting. Entrypoint used by uvicorn.
- routers/
  - weather.py — API endpoints for raw weather data (CRUD / listings).
  - stats.py — endpoints for aggregated statistics (annual summaries, etc).
- db/
  - models.py — SQLAlchemy models representing tables (Weather, etc).
  - create_db.py — helper to create DB schema (runs migrations or SQLAlchemy metadata.create_all()).
  - session.py — DB session maker and engine factory; central place for DATABASE_URL handling.
  - __init__.py — exports convenience objects for DB access.
- crud.py — functions that encapsulate DB operations (create, query, update) used by routers and tests.
- schemas.py — Pydantic request/response models for API payload validation.
- ingest.py — logic to fetch/parse weather files (S3 or local wx_data) and insert into DB.
- analysis.py — functions that compute derived statistics from stored data (annual aggregates, percentiles).

tests/
- test_models.py — simple unit tests for model/schema/DB behavior. Tests run inside the app container; ensure PYTHONPATH includes /code so the app package is importable.

---

## Common Troubleshooting

- ModuleNotFoundError: No module named 'app'
  - Ensure you run tests from src/ (project root in container is /code).
  - Use the Makefile test target or pass PYTHONPATH:
    ```
    docker compose run --rm -e PYTHONPATH=/code app pytest tests/
    ```

- importlib AttributeError (module 'importlib' has no attribute 'util')
  - This signals a local file named importlib.py or a package named importlib shadowing the stdlib.
  - Find and remove/rename it:
    ```
    docker compose run --rm -e PYTHONPATH=/code app bash -lc "find /code -maxdepth 4 \( -name 'importlib.py' -o -name 'importlib' -type d \) -print"
    ```

- Compose warning about `version` key
  - Remove the top-level version line from docker-compose.yml to silence the deprecation warning.

- Make reports "Nothing to be done for `test`"
  - Run from the directory containing the Makefile (src/), or force with:
    ```
    make -B test
    ```

---

## Notes & Suggestions

- Ensure the DATABASE_URL in .env points to the postgres service (when using compose: postgresql://postgres:password@postgres:5432/weatherdb or the value your setup uses).
- For local development, exposing PYTHONPATH=/code in docker-compose.environment ensures imports work consistently.
- Add a README section per endpoint (optional) or an OpenAPI reference update if API surface changes.

---
If you want, I can:
- add a short README section showing example curl requests for each endpoint, or
- generate a simple CONTRIBUTING or DEV_SETUP guide with step-by-step local development instructions.