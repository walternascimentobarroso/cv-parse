# Research: Testing Strategy for the Project

**Feature**: 003-testing-strategy  
**Date**: 2026-03-11

## Technology Choices

### Testing framework selection

- **Decision**: Use **pytest** as the single test runner. Use **FastAPI TestClient** (from `starlette.testclient`) or **httpx** for API tests. Add **pytest-cov** only if coverage reporting is adopted (see Coverage goals below).
- **Rationale**: pytest is already in `pyproject.toml` and is the de facto standard for Python; the project already has `tests/` with pytest and TestClient. No new runner or BDD framework is needed. TestClient runs the app in-process without a live server, satisfying “API tests without starting server” for local runs; CI can use the same. httpx is already a dependency and can be used for async or more control if needed; TestClient is sufficient for current scope.
- **Alternatives considered**: unittest (stdlib)—pytest is already in use and has better ergonomics (fixtures, markers). nose2 / tox—extra complexity; pytest alone with path-based or marker-based selection is enough. Chosen: pytest + TestClient; pytest-cov only if coverage goals are in scope.

### Project test structure

- **Decision**: Single top-level **tests/** directory with subdirectories **tests/domain/**, **tests/api/**, **tests/infra/** mirroring **src/domain/**, **src/api/**, **src/infra/**.
- **Rationale**: Matches spec “tests directory mirroring the project architecture” and constitution “simple folder structure.” One place for all tests; finding tests for a layer is trivial (same path as source). Naming: `test_<module>.py` under each layer (e.g. `tests/domain/test_extractor.py`, `tests/api/test_routes.py`, `tests/infra/test_storage.py`).
- **Alternatives considered**: Tests next to source (`src/domain/tests/`)—rejected to keep test code out of package and avoid shipping tests. Single flat `tests/` with prefixes—rejected in favor of mirror layout for clarity. Chosen: `tests/{domain,api,infra}/` with `test_*.py` modules.

### Separation between unit, integration, and API tests

- **Decision**:
  - **Unit (domain)**: Tests in **tests/domain/**; no application server, no real DB/storage/network. Use in-memory or mock implementations where the domain depends on abstractions (e.g. extractor protocol). Fast, no external setup.
  - **Integration (infra)**: Tests in **tests/infra/**; run against real or test doubles (e.g. in-memory MongoDB, temp dirs, or test containers). Fixtures in `conftest.py` (or layer-specific conftest) handle setup/teardown. Document any required env (e.g. `MONGODB_URI` for real DB) or that tests skip when unavailable.
  - **API**: Tests in **tests/api/**; use **TestClient** against the FastAPI app with dependencies overridden (e.g. in-memory repo, real extractor). No live HTTP server; exercise routes, status codes, and response bodies. Covers main success and critical error paths.
- **Rationale**: Clear boundaries per spec; domain stays pure, infra proves integration, API proves contract. Separation by directory allows “run by layer” (e.g. `pytest tests/domain/`) and keeps intent obvious.
- **Alternatives considered**: Pytest markers only (e.g. `@pytest.mark.unit`) without directory split—possible but layout mirroring is easier to navigate. Chosen: Directory-based separation with optional markers for filtering if needed later.

### Test execution workflow

- **Decision**:
  - **Full suite**: One command runs all tests, e.g. `uv run pytest tests/` (or `make test` delegating to that). Exit code 0 = all pass; non-zero = at least one failure; report shows test count and failures per path.
  - **By layer**: Run one layer at a time: `pytest tests/domain/`, `pytest tests/api/`, `pytest tests/infra/`. No new runner; same pytest, different path. Optional: `make test-unit`, `make test-api`, `make test-integration` (or similar) in Makefile for convenience.
  - **Isolation**: No shared mutable state across tests; fixtures scope (function/session) and cleanup (e.g. temp dirs, in-memory state) so order does not matter. Integration tests that need a real service MUST document it and SHOULD skip with a clear message if unavailable (e.g. `pytest.importorskip` or env check).
- **Rationale**: Single command for CI; by-layer for fast feedback. Document in quickstart and contracts so new developers and CI can run repeatably.
- **Alternatives considered**: Tox matrices—YAGNI for now; single pytest run is enough. Chosen: `pytest tests/` and `pytest tests/<layer>/`; optional Makefile targets.

### Test coverage goals

- **Decision**: Define **measurable coverage goals** as project policy, not enforced by CI initially (to avoid blocking on legacy gaps). Recommended: **domain layer** high (e.g. ≥ 80% line coverage for `src/domain/`); **api** main and critical error paths covered (target can be “all routes and key status codes”); **infra** critical paths covered. Use **pytest-cov** to report coverage; add `--cov=src/domain` (and optionally `src/api`, `src/infra`) when running. Coverage thresholds (e.g. `--cov-fail-under=80` for domain) can be enabled later once baseline is met.
- **Rationale**: Spec asks for “test coverage goals”; constitution favors testable code. Starting with explicit goals and optional reporting keeps scope bounded; enforcing thresholds can be a follow-up.
- **Alternatives considered**: No coverage tool—rejected so that goals are measurable. Strict fail-under from day one—rejected to avoid blocking on existing code. Chosen: pytest-cov for reporting; document goals (domain ≥ 80%, api/infra critical paths); optional `--cov-fail-under` when baseline is reached.

## Resolved Items

- **Framework**: pytest; FastAPI TestClient for API tests; pytest-cov for coverage reporting and goals.
- **Structure**: `tests/` with `tests/domain/`, `tests/api/`, `tests/infra/` mirroring `src/`.
- **Separation**: Unit = domain (no server/externals); Integration = infra (real or test doubles, documented setup); API = api (TestClient, overridden deps).
- **Execution**: Full suite = `pytest tests/`; by layer = `pytest tests/<layer>/`; optional Makefile targets; isolation and skip policy for missing externals.
- **Coverage**: Goals documented (domain ≥ 80%, api/infra critical paths); pytest-cov; optional fail-under once baseline met.

All Technical Context items from the plan are defined. Constitution gates (single responsibility, YAGNI, testable isolated code, explicit boundaries) are respected.
