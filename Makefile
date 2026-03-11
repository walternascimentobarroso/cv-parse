.PHONY: install up down recreate logs run test lint deactivate

install:
	uv sync

up:
	docker compose up -d

down:
	docker compose down

recreate:
	docker compose down && docker compose up -d --build

logs:
	docker compose logs -f

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .

# Exit the virtual environment (run 'deactivate' in your shell for the current session)
deactivate:
	deactivate
