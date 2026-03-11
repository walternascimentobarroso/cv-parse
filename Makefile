.PHONY: install up down logs run test lint

install:
	uv sync

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .

