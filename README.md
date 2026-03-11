# Doc-to-Text API – Development Environment

This repository contains a small Doc-to-Text API and an improved development environment focused on fast onboarding and simple workflows.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package/dependency manager)
- Docker and Docker Compose

## Getting started

From the repo root:

```bash
cp .env.example .env
make install
make up
```

This installs dependencies with uv and starts the API and MongoDB. The API is available at `http://localhost:8000`.

## Makefile commands

- `make install` – Install dependencies from `pyproject.toml` / `uv.lock`
- `make up` – Start services with Docker Compose
- `make down` – Stop and remove containers
- `make logs` – Follow service logs
- `make run` – Run the app locally with uv
- `make test` – Run tests
- `make lint` – Run Ruff

## Environment configuration

Environment variables are defined in `.env` (not committed) with `.env.example` as the template. Both the app and Docker Compose read from `.env` so configuration is consistent.

See `specs/002-dev-env-tooling/quickstart.md` and `specs/002-dev-env-tooling/contracts/env.md` for details.

