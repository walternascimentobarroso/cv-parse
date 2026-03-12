# Quickstart: Testing

**Feature**: 003-testing-strategy  
**Date**: 2026-03-11

This guide describes how to run the test suite, run tests by layer, and (optionally) generate coverage reports.

## Prerequisites

- Dependencies installed: `make install` or `uv sync` (see main project quickstart if needed).
- No running services required for **domain** or **API** tests (they use in-process TestClient and in-memory doubles).
- **Integration tests** (infra): may require env (e.g. `MONGODB_URI`) or use in-memory/test doubles; see [Test environment](#test-environment) below.

## Running tests

### Full suite

Run all tests (domain, api, infra):

```bash
uv run pytest tests/
```

Or, if the Makefile exposes it:

```bash
make test
```

You get a single consolidated result: number of tests run, passed, failed, and any failure details.

### By layer

Run only one layer for fast feedback:

| Layer     | Command                     | Use case |
|-----------|-----------------------------|----------|
| Domain    | `uv run pytest tests/domain/` | Unit tests; no server or externals. |
| API       | `uv run pytest tests/api/`    | HTTP endpoint tests (TestClient). |
| Infra     | `uv run pytest tests/infra/`   | Integration tests (storage, config, etc.). |

Optional Makefile targets (if present): `make test-unit`, `make test-api`, `make test-integration`.

## Test layout

Tests mirror the source structure:

- **tests/domain/** — unit tests for `src/domain/` (e.g. extractor logic).
- **tests/api/** — API tests for `src/api/` (routes, status codes, responses).
- **tests/infra/** — integration tests for `src/infra/` (e.g. repository + DB or in-memory).

Shared fixtures (e.g. TestClient, in-memory repo) live in **tests/conftest.py**. See [contracts/test-layout.md](./contracts/test-layout.md) for the full layout and naming rules.

## Test environment

- **Domain**: No env or services. Pure in-process; mocks or in-memory implementations only.
- **API**: App runs in-process with dependency overrides (in-memory repo, extractor). No live server; TestClient only.
- **Infra**: Depends on implementation. If tests use a real MongoDB (or other service), set the required env (e.g. `MONGODB_URI`) or use test doubles. If the service is unavailable, integration tests may **skip** with a clear message instead of failing.

## Coverage (optional)

With **pytest-cov** installed, run tests with coverage:

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

Domain-only coverage:

```bash
uv run pytest tests/domain/ --cov=src/domain --cov-report=term-missing
```

Coverage goals (see [research.md](./research.md)): domain layer ≥ 80% line coverage; API and infra critical paths covered. Enforcing a minimum (e.g. `--cov-fail-under=80`) is optional and can be enabled once the baseline is met.

## Troubleshooting

- **Import errors**: Ensure you run from repo root and deps are installed (`uv sync`).
- **API tests fail**: Ensure `conftest.py` overrides app dependencies (e.g. in-memory repo); no real DB needed.
- **Integration tests skip or fail**: Check env (e.g. `MONGODB_URI`) or switch to in-memory/test doubles; see [contracts/test-commands.md](./contracts/test-commands.md) and [data-model.md](./data-model.md).

## References

- [Test layout contract](./contracts/test-layout.md) — directory structure and naming.
- [Test commands contract](./contracts/test-commands.md) — full list of commands and optional Makefile targets.
- [Data model](./data-model.md) — test suite by layer, layout, and test environment.
