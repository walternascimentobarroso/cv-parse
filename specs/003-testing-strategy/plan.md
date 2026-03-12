# Implementation Plan: Testing Strategy for the Project

**Branch**: `003-testing-strategy` | **Date**: 2026-03-11 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/003-testing-strategy/spec.md`

## Summary

Introduce a structured testing strategy that covers the three DDD layers (api, domain, infra) with automated unit tests for domain logic, integration tests for infrastructure, and API tests for HTTP endpoints. Tests live in a dedicated top-level `tests/` directory whose structure mirrors `src/` (e.g. `tests/domain/`, `tests/api/`, `tests/infra/`). The project supports running the full suite in one command and running tests by layer for fast feedback. Test execution workflow, coverage goals, and setup are documented so developers and CI can run tests repeatably. Aligns with constitution: testable isolated code, explicit boundaries (tests per layer), single responsibility (each test category has one purpose), minimal tooling (one test runner, one layout).

## Technical Context

**Language/Version**: Python 3.12 (existing)  
**Primary Dependencies**: FastAPI, motor, pdfplumber, pydantic-settings (existing); pytest, httpx already in pyproject.toml  
**Testing**: pytest as test runner; FastAPI TestClient (or httpx) for API tests; coverage tool (e.g. pytest-cov) for coverage goals  
**Target Platform**: Local development (macOS/Linux), CI; tests run in-process or with test doubles; integration tests may use in-memory or test instances  
**Project Type**: Web service (doc-to-text API) with DDD layers: api, domain, infra  
**Constraints**: Tests MUST be isolated (no order dependency); domain tests MUST NOT start server or use real external systems; integration tests MUST have documented setup/teardown  
**Scale/Scope**: Single repo; one test directory mirroring src; three test categories (unit, integration, API)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility**: Each test layer has one purpose—domain tests verify business logic in isolation, infrastructure tests verify integration with externals, API tests verify HTTP contract. Test modules are organized by layer.
- **YAGNI / Simplicity**: Only the test categories and layout specified (unit for domain, integration for infra, API for endpoints). No extra test frameworks or runners beyond pytest and existing deps; coverage tool only if coverage goals are adopted.
- **Testable, Isolated**: Strategy enforces isolation (domain tests no server/externals; integration tests use test doubles or dedicated test env; API tests use TestClient). Shared state is reset or isolated per test/suite.
- **Explicit Boundaries**: Test layout mirrors source layout (api, domain, infra); running by layer is explicit (e.g. path or marker). Documentation and contracts describe how to run each category and what setup is required.
- **Readability**: Test directory and file names reflect the layer and intent; quickstart and contracts document commands and conventions.
- **Clean Code constraints**: Limited scope to testing strategy (framework, structure, separation, workflow, coverage); minimal new dependencies (pytest/cov only as needed); no premature optimization (coverage goals are measurable and achievable).

*Post–Phase 1*: Research resolves framework choices (pytest, coverage), structure (mirror layout), and execution workflow. Data-model and contracts document test layout and run commands. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-testing-strategy/
├── plan.md              # This file
├── research.md          # Phase 0 (framework, structure, workflow, coverage)
├── data-model.md        # Phase 1 (test suite by layer, layout, test environment)
├── quickstart.md        # Phase 1 (how to run tests, setup)
├── contracts/           # Phase 1 (test layout, test run commands)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

Test directory mirrors `src/` layout. Existing flat `tests/` is reorganized into layer-aligned subdirs.

```text
# Repository root
tests/
├── conftest.py              # Shared fixtures (e.g. test client, in-memory repo)
├── domain/                  # Unit tests for domain layer
│   ├── __init__.py
│   └── test_extractor.py    # (e.g. extractor behavior, validation)
├── api/                     # API tests (HTTP endpoints)
│   ├── __init__.py
│   └── test_routes.py       # (e.g. health, extract success/error paths)
└── infra/                   # Integration tests for infrastructure
    ├── __init__.py
    └── test_storage.py      # (e.g. repository + test DB or in-memory)
```

**Structure Decision**: One top-level `tests/` directory. Subdirectories `tests/domain/`, `tests/api/`, `tests/infra/` mirror `src/domain/`, `src/api/`, `src/infra/`. Domain = unit (no server/externals); api = endpoint tests (TestClient); infra = integration (real or test doubles). Full suite = `pytest tests/`; by layer = `pytest tests/domain/`, `pytest tests/api/`, `pytest tests/infra/`.

## Complexity Tracking

No constitution violations requiring justification. One test runner (pytest), one layout (mirror src), three clear test categories.
