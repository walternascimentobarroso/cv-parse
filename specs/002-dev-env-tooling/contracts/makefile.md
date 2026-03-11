# Contract: Makefile Developer Commands

**Feature**: 002-dev-env-tooling  
**Date**: 2025-03-11

## Purpose

The Makefile at repository root exposes a single command surface for common developer tasks. All targets are phony; implementation may delegate to `uv` and `docker compose`.

## Required targets

| Target    | Command (reference)     | Description |
|----------|--------------------------|-------------|
| **install** | `uv sync`              | Install Python dependencies from `uv.lock`. Run once after clone or when dependencies change. |
| **up**      | `docker compose up -d`  | Start all services in the background. Idempotent: safe to run when already up; may report "already running" or start only missing containers. |
| **down**    | `docker compose down`   | Stop and remove containers. Idempotent: safe when nothing is running. |
| **logs**    | `docker compose logs -f`| Stream logs from all services. Follow mode; exit with Ctrl+C. |

## Optional targets (recommended)

| Target | Command (reference) | Description |
|--------|--------------------|-------------|
| **run**  | `uv run uvicorn src.main:app --reload ...` | Run the application locally (no Docker), using env from `.env`. |
| **test** | `uv run pytest`     | Run the test suite. |
| **lint** | `uv run ruff check .` | Lint the codebase. |

## Preconditions

- **install**: Requires `uv` installed; expects `pyproject.toml` and `uv.lock` at repo root.
- **up**, **down**, **logs**: Require Docker and Docker Compose; expect `docker-compose.yml` and `.env` at repo root. If `.env` is missing, Compose may fail or use empty env; document in quickstart that `.env` must exist (copy from `.env.example`).

## Error behavior

- If `uv` or `docker compose` is missing, the Makefile SHOULD fail with a clear message (e.g. "uv not found; install from ...").
- If `.env` is missing and required for a target, document in quickstart; optional: add a target that checks for `.env` and prints a reminder.
