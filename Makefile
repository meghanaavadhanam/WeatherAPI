.PHONY: test lint format

test:
	docker compose run --rm -e PYTHONPATH=/code app pytest tests/

lint:
	docker run --rm -v $(PWD):/app -w /app python:3.10-slim bash -lc "pip install --no-cache-dir ruff && ruff check app tests"

format:
	docker run --rm -v $(PWD):/app -w /app python:3.10-slim bash -lc "pip install --no-cache-dir black && black app/ tests/"