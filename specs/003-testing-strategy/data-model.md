# Data Model: Testing Strategy

**Feature**: 003-testing-strategy  
**Date**: 2026-03-11

## Overview

This feature does not introduce new application data entities. It defines the **test suite (by layer)**, **test layout**, and **test environment** as the conceptual model that developers and CI use to run and organize automated tests.

## Entities

### Test suite (by layer)

The set of tests that target one architectural layer (domain, infrastructure, or API). Used to run fast feedback for one layer or to group tests in reports.

| Attribute     | Description |
|---------------|-------------|
| **Domain**    | Unit tests in `tests/domain/`. No application server or real external systems. Exercises business logic in isolation. |
| **API**       | API tests in `tests/api/`. Sends HTTP requests via TestClient; asserts status codes and response content. Dependencies (repo, extractor) overridden for in-process testing. |
| **Infra**     | Integration tests in `tests/infra/`. Uses real or test doubles (e.g. in-memory storage, test DB). Setup/teardown documented or automated. |

**Rules**:

- Running the full suite MUST execute all three layers and report a consolidated result.
- Running by layer MUST be supported (e.g. `pytest tests/domain/`, `pytest tests/api/`, `pytest tests/infra/`).
- Test outcome MUST be independent of execution order; shared state MUST be reset or isolated per test or suite.

### Test layout

The directory and module structure under the dedicated test directory, mirroring the source layout (api, domain, infra) so that tests are easy to find and maintain.

| Attribute     | Description |
|---------------|-------------|
| **Root**      | Single top-level directory `tests/` at repository root. |
| **Subdirs**   | `tests/domain/`, `tests/api/`, `tests/infra/` corresponding to `src/domain/`, `src/api/`, `src/infra/`. |
| **Naming**    | Test modules: `test_<module>.py` (e.g. `test_extractor.py`, `test_routes.py`, `test_storage.py`). Test functions: `test_<behavior>` (pytest convention). |
| **Shared**    | `tests/conftest.py` holds shared fixtures (e.g. TestClient, in-memory repository, extractor). Layer-specific `conftest.py` allowed under `tests/<layer>/` if needed. |

**Rules**:

- New tests for a layer MUST be added under the corresponding `tests/<layer>/` directory.
- Layout MUST remain a direct mirror of the source layers (no extra top-level categories beyond domain, api, infra).

### Test environment

The configuration and dependencies required to run integration and API tests; must be documented and, where possible, automated.

| Attribute       | Description |
|-----------------|-------------|
| **Unit (domain)** | No external services. In-process only; mocks or in-memory implementations for any dependency. |
| **API**           | FastAPI app with dependency overrides (e.g. in-memory repo, real or stub extractor). TestClient; no live network server. |
| **Integration**   | Real or test doubles: e.g. in-memory MongoDB, temp directories, or test instance. Env vars (e.g. `MONGODB_URI`) documented; tests MAY skip with clear message if dependency unavailable. |

**Rules**:

- Domain tests MUST NOT require env vars or running services.
- API tests MUST run with overridden dependencies so no real DB or external service is required for the default run.
- Integration tests that require a real service MUST document the requirement and SHOULD skip gracefully when unavailable (e.g. env check or pytest skip).

## Out of scope

- Multiple test frameworks (e.g. pytest + unittest in parallel); one runner (pytest) only.
- BDD or Gherkin; plain pytest test functions and modules.
- Coverage enforcement in CI until baseline meets goals (coverage reporting and goals are in scope; fail-under is optional follow-up).
