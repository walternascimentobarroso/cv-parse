# Contract: Test Run Commands

**Feature**: 003-testing-strategy  
**Date**: 2026-03-11

## Purpose

The project supports running the full test suite in one command and running tests by layer. Commands are reproducible by any developer and by CI.

## Required commands

| Intent        | Command (reference)     | Description |
|---------------|--------------------------|-------------|
| **Full suite**| `uv run pytest tests/`   | Run all tests (domain, api, infra). Exit 0 = all pass; non-zero = at least one failure. Report shows test count and failures. |
| **Domain only** | `uv run pytest tests/domain/` | Run only domain (unit) tests. No server or external services required. |
| **API only**  | `uv run pytest tests/api/`    | Run only API tests (TestClient). No live server. |
| **Infra only**| `uv run pytest tests/infra/`  | Run only infrastructure integration tests. May require env or test doubles; see quickstart for setup. |

## Optional Makefile targets

If the project uses a Makefile (see 002-dev-env-tooling), the following targets MAY be added for convenience:

| Target           | Command (reference)        | Description |
|------------------|----------------------------|-------------|
| **test**         | `uv run pytest tests/`     | Run full suite (may already exist). |
| **test-unit**    | `uv run pytest tests/domain/` | Run domain unit tests only. |
| **test-api**     | `uv run pytest tests/api/`   | Run API tests only. |
| **test-integration** | `uv run pytest tests/infra/` | Run integration tests only. |

## Coverage (optional)

When coverage reporting is enabled (pytest-cov):

| Intent     | Command (reference) | Description |
|------------|---------------------|-------------|
| **Report** | `uv run pytest tests/ --cov=src --cov-report=term-missing` | Run all tests and print coverage for `src/`. |
| **Domain coverage** | `uv run pytest tests/domain/ --cov=src/domain --cov-report=term-missing` | Coverage for domain layer only. |

Coverage goals (see research.md): domain ≥ 80% line coverage; api and infra critical paths covered. Thresholds (e.g. `--cov-fail-under=80`) are optional and can be enabled once baseline is met.

## Preconditions

- **Full suite / Domain / API**: No external services required. Dependencies installed (`make install` or `uv sync`).
- **Infra**: May require env (e.g. `MONGODB_URI` for real MongoDB) or in-memory/test doubles; see quickstart. If a required service is unavailable, integration tests SHOULD skip with a clear message rather than fail hard.

## Error behavior

- If pytest or project deps are missing, the command fails (e.g. "pytest not found" or import errors). Developer runs `uv sync` (or `make install`).
- If a test fails, pytest exits non-zero and prints the failing test(s) and traceback.
- If integration tests depend on a service that is down, they MAY skip (e.g. `pytest.skip` or env check) with a message so CI or developer knows why.
