# Data Model: Development Environment and Tooling

**Feature**: 002-dev-env-tooling  
**Date**: 2025-03-11

## Overview

This feature does not introduce new application data entities. It defines the **environment configuration** (key-value pairs consumed by the app and Compose) and the **developer command surface** (Makefile targets) as the conceptual “model” that developers and tooling interact with.

## Entities

### Environment configuration

The set of named variables used to configure the application and containerized services. Stored in a single file (`.env`) at repository root; not persisted in a database.

| Attribute    | Description |
|-------------|-------------|
| **Source**  | `.env` at repo root (gitignored); `.env.example` committed as template |
| **Format**  | Key=value lines; same names as application settings (e.g. `MONGODB_URI`, `MONGODB_DB`) |
| **Consumer**| Application (via pydantic-settings / `Settings`); Docker Compose (via `env_file: .env`) |

**Rules**:

- Required variables MUST be documented in `.env.example` and in the contracts.
- Missing or invalid values SHOULD produce a clear error at startup (app or Compose).
- No secrets in `.env.example`; only placeholder or example values.

### Developer command surface

The set of Makefile targets that developers use to install dependencies, run services, and view logs. No persistent state; each target maps to a single action (e.g. `uv sync`, `docker compose up -d`).

| Target     | Purpose |
|-----------|---------|
| **install** | Install Python dependencies from lockfile (uv sync) |
| **up**      | Start containerized services (docker compose up -d) |
| **down**    | Stop and remove containers (docker compose down) |
| **logs**    | Stream service logs (docker compose logs -f) |

Optional targets (run, test, lint) may be added; the spec requires at least up, down, logs and a documented install flow.

**Rules**:

- Targets MUST be idempotent or clearly report state (e.g. “already running”).
- Targets MUST be documented in contracts and quickstart so a new developer can run them without reading the underlying tool docs.

## Out of scope

- Multiple env files per environment (e.g. .env.dev, .env.prod); one `.env` at root is sufficient for this feature.
- Secrets management (Vault, etc.); secrets stay in `.env` (gitignored) or are injected by the environment.
- New application domain entities; only tooling and config layout are in scope.
