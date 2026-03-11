# Research: Improve Development Environment and Project Tooling

**Feature**: 002-dev-env-tooling  
**Date**: 2025-03-11

## Technology Choices

### Replace pip with uv

- **Decision**: Use **uv** as the single Python package manager. Migrate from `requirements.txt` to `pyproject.toml` for dependency declaration; use `uv.lock` for locked, reproducible installs.
- **Rationale**: uv is fast, pip-compatible, and supports lockfiles natively. One tool for install/sync/run reduces setup steps and aligns with “single package manager” in the spec. Python 3.12 is already in use (from 001).
- **Alternatives considered**: Keeping pip + pip-tools (adds another tool); Poetry (heavier; uv is lighter and lockfile is standard). Chosen: uv for speed, simplicity, and lockfile support.

### Dependency lock strategy

- **Decision**: Maintain a single **uv.lock** at repo root; commit it to version control. Use `uv lock` to create/update the lockfile; use `uv sync` (or `uv sync --frozen` in CI/Docker) to install from the lockfile so every environment gets the same versions.
- **Rationale**: Reproducible builds and “works the same everywhere”; avoids drift between dev and CI/Docker. `--frozen` fails if lockfile is out of date, which is desirable in CI.
- **Alternatives considered**: No lockfile (rejected: spec asks for reproducible setup); exporting to requirements.txt for Docker only (rejected: prefer single source of truth in uv.lock). Chosen: uv.lock committed; Dockerfile uses uv to install from lockfile.

### Environment variable management with .env

- **Decision**: Single **.env** file at repository root. Commit **.env.example** with documented variable names and example (non-secret) values. Application loads env via **pydantic-settings** (already in 001) from the process environment; locally, developers (or the Makefile) ensure `.env` is loaded before running the app (e.g. `set -a; source .env; set +a` or a small loader). Do not commit `.env` (remain in `.gitignore`).
- **Rationale**: One place for local config; same variable names for app and Docker Compose; pydantic-settings already reads `os.environ`, so we only need to populate it from `.env` in dev and from Compose in containers.
- **Alternatives considered**: Multiple env files per environment (rejected for v1: YAGNI; one file + .env.example is enough). Chosen: one `.env` at root, one `.env.example` committed, app uses existing settings pattern.

### Docker Compose integration

- **Decision**: Configure Compose to read the same env file via **env_file: .env** (path relative to compose file). Remove hardcoded `environment:` entries that duplicate values that should come from `.env`; keep only overrides or defaults that are not in .env. Use the same variable names in `.env.example` and in the app so Compose, local runs, and the app all see the same config.
- **Rationale**: Single source of truth; “Docker Compose reads configuration from the .env file” per spec. Compose loads `.env` automatically for variable substitution in the compose file and can pass them to services via `env_file`.
- **Alternatives considered**: Inline env in compose only (rejected: duplicates app config). Chosen: `env_file: .env`; document that `docker compose up` (or `make up`) expects `.env` at repo root.

### Makefile developer commands

- **Decision**: Add a **Makefile** at repo root with at least: **install** (uv sync), **up** (docker compose up -d), **down** (docker compose down), **logs** (docker compose logs -f). Optionally: **run** (run app locally with uv), **test** (uv run pytest), **lint** (uv run ruff). Use phony targets and document in quickstart.
- **Rationale**: One command surface for common tasks; “make up”, “make down”, “make logs” are easy to remember and match the spec. No new runtime dependency (make is standard on macOS/Linux).
- **Alternatives considered**: Just (or task runners): additional tool to install. Chosen: Makefile for maximum portability and zero extra install.

## Resolved Items

- **Package manager**: uv; dependencies in pyproject.toml; lockfile uv.lock committed.
- **Env**: .env at root; .env.example committed; app loads via pydantic-settings; Compose uses env_file: .env.
- **Commands**: Makefile with install, up, down, logs (and optionally run, test, lint).
- **Docker**: Dockerfile uses uv to install from lockfile; Compose reads .env so app and containers share config.

All Technical Context items from the plan are defined. Constitution gates (single responsibility, YAGNI, minimal deps, explicit boundaries) are respected.
