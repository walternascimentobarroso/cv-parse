# Quickstart: Development Environment Setup

**Feature**: 002-dev-env-tooling  
**Date**: 2025-03-11

This guide gets a new developer from clone to running services using uv, `.env`, and the Makefile.

## Prerequisites

- **uv**: [Install uv](https://docs.astral.sh/uv/getting-started/installation/) (Python is managed by uv; no need to install Python separately for local dev).
- **Docker & Docker Compose**: For running the API and MongoDB in containers.

## Setup (first time)

1. **Clone** the repository and `cd` to the repo root.

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set values as needed (defaults in `.env.example` are valid for local Docker runs).

3. **Install dependencies** (from lockfile):
   ```bash
   make install
   ```
   This runs `uv sync` and installs the project dependencies. No pip or manual venv step.

4. **Start services**:
   ```bash
   make up
   ```
   This starts the API and MongoDB in the background. The API is available at `http://localhost:8000`.

5. **Optional – run app locally** (without Docker):
   ```bash
   make run
   ```
   Requires `.env` to be loaded (Makefile or your shell should source it). MongoDB must still be running (e.g. `make up` for DB only, or point `MONGODB_URI` to a local/remote instance).

## Daily commands

| Command     | Description |
|------------|-------------|
| `make up`  | Start all services (idempotent). |
| `make down`| Stop and remove containers. |
| `make logs`| Stream logs from all services (Ctrl+C to exit). |
| `make test`| Run tests (optional target). |
| `make lint`| Run linter (optional target). |

## Environment variables

See [contracts/env.md](./contracts/env.md) for the full list. Required for Docker: `MONGODB_URI`, `MONGODB_DB`. Copy `.env.example` to `.env` and adjust if needed.

## Troubleshooting

- **"uv: command not found"**: Install uv (see Prerequisites).
- **Compose fails or services miss config**: Ensure `.env` exists at repo root (copy from `.env.example`).
- **App fails at startup with config error**: Check that the variable names in `.env` match those in [contracts/env.md](./contracts/env.md); required variables must be set.

## Contract and layout

- **Makefile targets**: [contracts/makefile.md](./contracts/makefile.md)  
- **Env vars**: [contracts/env.md](./contracts/env.md)  
- **Plan and research**: [plan.md](./plan.md), [research.md](./research.md)
