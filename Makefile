# Color Config
NOCOLOR=\033[0m
GREEN=\033[0;32m
BGREEN=\033[1;32m
YELLOW=\033[0;33m
CYAN=\033[0;36m
RED=\033[0;31m

.PHONY: install up down recreate logs run test test-unit test-api test-integration lint deactivate clear-branches

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
	docker compose exec api uv run pytest --cov=src --cov-report=term-missing tests/

test-unit:
	uv run pytest tests/domain/

test-api:
	uv run pytest tests/api/

test-integration:
	uv run pytest tests/infra/

lint:
	uv run ruff check .

# Exit the virtual environment (run 'deactivate' in your shell for the current session)
deactivate:
	deactivate

clear-branches:
	@echo ""
	@git pull; git branch | grep -vE "(^\*|master|main|develop)" | xargs -r git branch -d
	@echo ""
	@echo "${GREEN}All old merged removed!${NOCOLOR}"
	@echo ""
