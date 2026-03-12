# Tasks: Testing Strategy for the Project

**Input**: Design documents from `/specs/003-testing-strategy/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3, US4 (user stories from spec.md)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Testing framework and structure)

**Purpose**: Configure the test framework and create the tests directory layout.

- [X] T001 Verify pytest is listed in dependencies in pyproject.toml and add pytest-cov if coverage is desired
- [X] T002 [P] Create directory tests/domain/ at repository root per specs/003-testing-strategy/contracts/test-layout.md
- [X] T003 [P] Create directory tests/api/ at repository root per specs/003-testing-strategy/contracts/test-layout.md
- [X] T004 [P] Create directory tests/infra/ at repository root per specs/003-testing-strategy/contracts/test-layout.md
- [X] T005 [P] Add tests/domain/__init__.py, tests/api/__init__.py, tests/infra/__init__.py to make packages discoverable

---

## Phase 2: Foundational (Shared test configuration)

**Purpose**: Define shared fixtures and configuration so all test layers can run.

- [X] T006 Define or consolidate shared fixtures (TestClient, in-memory repo, extractor) in tests/conftest.py per data-model.md
- [X] T007 Ensure tests/conftest.py overrides get_repo and get_extractor for API tests so no real DB is required
- [X] T008 Move existing tests from tests/test_domain.py into tests/domain/test_extractor.py preserving behavior
- [X] T009 Move existing tests from tests/test_api.py into tests/api/test_routes.py preserving behavior and client fixture usage
- [X] T010 Remove or deprecate tests/test_domain.py and tests/test_api.py after migration so only the new layout is used

**Checkpoint**: Full suite runs via `uv run pytest tests/` with new layout; domain and API tests pass.

---

## Phase 3: User Story 1 - Automated Verification of Domain Logic (Priority: P1) 🎯 MVP

**Goal**: Unit tests for domain layer; no server or external systems.

**Independent Test**: `uv run pytest tests/domain/` passes without starting the app or external services.

- [ ] T011 [P] [US1] Add unit tests in tests/domain/test_extractor.py for unsupported content type and empty content edge cases
- [ ] T012 [US1] Ensure tests/domain/test_extractor.py uses only in-memory data and no application server (per spec FR-001)

**Checkpoint**: Domain suite runs in under one minute and covers extractor behavior and edge cases.

---

## Phase 4: User Story 2 - Automated Verification of Infrastructure (Priority: P2)

**Goal**: Integration tests for infrastructure (e.g. storage) with real or test doubles.

**Independent Test**: `uv run pytest tests/infra/` runs and verifies repository/storage behavior; skip with clear message if dependency unavailable.

- [ ] T013 [P] [US2] Create tests/infra/test_storage.py with integration tests for ExtractionRepository in src/infra/storage.py
- [ ] T014 [US2] Add fixtures in tests/conftest.py or tests/infra/conftest.py for test MongoDB or in-memory double for ExtractionRepository
- [ ] T015 [US2] Document required env (e.g. MONGODB_URI) for infra tests in specs/003-testing-strategy/quickstart.md and add skip logic when unavailable
- [ ] T016 [US2] Ensure infra tests reset or isolate state so execution order does not affect results (per FR-007)

**Checkpoint**: Infrastructure tests validate storage behavior; setup/teardown documented; tests skip gracefully when service unavailable.

---

## Phase 5: User Story 3 - Automated Verification of API Endpoints (Priority: P3)

**Goal**: API tests that hit routes via TestClient and assert status and response body.

**Independent Test**: `uv run pytest tests/api/` passes and covers main success and critical error paths.

- [ ] T017 [P] [US3] Confirm tests/api/test_routes.py covers /health and /extract success path and critical errors (missing file, unsupported format, too large, internal error)
- [ ] T018 [US3] Ensure tests/api/test_routes.py uses client fixture from tests/conftest.py and does not require real DB or server

**Checkpoint**: API tests cover main and critical error paths; failures indicate route/validation regressions.

---

## Phase 6: User Story 4 - Clear Test Organization (Priority: P4)

**Goal**: Test layout mirrors src/ (domain, api, infra); easy to find where to add tests.

**Independent Test**: New contributor can locate tests for src/domain, src/api, src/infra within one minute.

- [ ] T019 [US4] Verify tests/domain/, tests/api/, tests/infra/ mirror src/domain/, src/api/, src/infra/ and update specs/003-testing-strategy/contracts/test-layout.md if needed
- [ ] T020 [US4] Ensure specs/003-testing-strategy/quickstart.md describes final layout and commands for full suite and by-layer runs

**Checkpoint**: Layout is clear and documented; contracts and quickstart match reality.

---

## Phase 7: Test execution commands (Polish)

**Purpose**: Configure full-suite and by-layer test execution and optional coverage.

- [X] T021 Configure Makefile test target to run `uv run pytest tests/` (full suite) per specs/003-testing-strategy/contracts/test-commands.md
- [X] T022 [P] Add optional Makefile targets test-unit, test-api, test-integration pointing to tests/domain/, tests/api/, tests/infra/
- [X] T023 [P] Document coverage command (e.g. `uv run pytest tests/ --cov=src --cov-report=term-missing`) and goals in specs/003-testing-strategy/quickstart.md

---

## Dependencies

- Phase 1–2 must complete before Phase 3–6.
- US1 (Phase 3) is MVP; US2 and US3 (Phases 4–5) can proceed in parallel after Phase 2.
- Phase 7 can run after Phases 3–6.

## Implementation strategy

- **MVP**: Phase 1 + Phase 2 + Phase 3 (framework, layout, shared config, domain unit tests).
- **Incremental**: Add Phase 4 (infra), Phase 5 (API), Phase 6 (organization docs), Phase 7 (commands) in order or in parallel for 4–5 once 2 is done.
