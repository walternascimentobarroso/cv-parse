---
description: "Implementation tasks for 004-cv-api-refactor"
---

# Tasks: CV Extraction API Refactor (004-cv-api-refactor)

**Input**: Design documents from `/specs/004-cv-api-refactor/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/api.md`, `quickstart.md`

**Organization**: Tasks are grouped by phase and user story. Each task line follows:

```text
- [ ] TNNN [P?] [US?] Description with file path
```

Below each task, details list goal, files affected, and expected outcome.

---

## Phase 1: Setup & Foundational Infrastructure

**Purpose**: Introduce core modules and wiring required for all user stories, without changing external behavior.

- [X] T001 Introduce constants modules for MIME types and collection names in src/domain/constants.py and src/infra/constants.py
  - **Goal**: Remove magic strings by centralizing MIME types and MongoDB collection names.
  - **Files**: src/domain/constants.py, src/infra/constants.py, src/infra/config.py, src/infra/storage.py
  - **Expected outcome**: MIME types and collection names are defined once and imported where needed; no behavioral change.

- [X] T002 [P] Wire collection constants into MongoDB repository and main app in src/infra/storage.py and src/main.py
  - **Goal**: Ensure the extraction collection name is used via constants instead of inline strings.
  - **Files**: src/infra/storage.py, src/main.py
  - **Expected outcome**: Repository and MongoDB collection selection rely on `EXTRACTIONS_COLLECTION` (or equivalent) constant with same effective collection as before.

- [X] T003 [P] Replace MIME type string literals with constants in config and extractor in src/infra/config.py and src/domain/extractor.py
  - **Goal**: Eliminate hard-coded MIME strings and use shared domain constants for PDF and plain text.
  - **Files**: src/infra/config.py, src/domain/extractor.py, src/api/routes.py
  - **Expected outcome**: Allowed content types and extractor logic use domain MIME constants; supported formats remain unchanged.

- [X] T004 Create centralized logging configuration module in src/infra/logging_config.py and integrate in src/main.py
  - **Goal**: Configure structured logging (JSON or key-value) once and reuse across routes, validators, and extractors.
  - **Files**: src/infra/logging_config.py, src/main.py
  - **Expected outcome**: Application initializes a consistent logging setup; existing behavior unaffected aside from additional logs.

- [X] T005 Define domain interfaces module for extractors in src/domain/document_extractor_contracts.py
  - **Goal**: Move Protocol definitions (e.g., extractor interface) into a dedicated domain module.
  - **Files**: src/domain/document_extractor_contracts.py, src/domain/extractor.py
  - **Expected outcome**: Domain contracts are declared in `document_extractor_contracts.py`, and existing extractor implementation conforms without behavior change.

- [X] T006 Create services package and upload validator skeleton in src/services/__init__.py and src/services/upload_validator.py
  - **Goal**: Establish a dedicated validation/service layer to host upload validation logic.
  - **Files**: src/services/__init__.py, src/services/upload_validator.py
  - **Expected outcome**: A validator module exists with function signatures for upload validation; routes not yet refactored to use it.

- [X] T007 Introduce FastAPI dependency providers module in src/api/dependencies.py
  - **Goal**: Centralize repository, extractor, and validator dependency providers for DI.
  - **Files**: src/api/dependencies.py
  - **Expected outcome**: `get_repo`, `get_extractor`, and `get_upload_validator` (or equivalent) functions exist and can be wired from `app.state`.

---

## Phase 2: User Story 1 – Upload and Extract Preserved (Priority: P1) [US1] 🎯 MVP

**Goal**: Preserve the current `/extract` behavior (contract and storage) while introducing response schemas, validators, and DI without breaking clients.

**Independent Test**: Call `POST /extract` with valid PDF and TXT files and confirm responses and storage match pre-refactor behavior.

- [X] T008 [US1] Implement upload validation logic in src/services/upload_validator.py
  - **Goal**: Move file presence, content type, and size checks from routes into the validator service.
  - **Files**: src/services/upload_validator.py
  - **Expected outcome**: Validator returns a result type (success or error) based on file validity, using MIME constants and configured size limits.

- [X] T009 [US1] Refactor src/api/routes.py to delegate upload validation to services/upload_validator.py
  - **Goal**: Keep routes thin by calling the validator instead of performing validation inline.
  - **Files**: src/api/routes.py, src/services/upload_validator.py
  - **Expected outcome**: `/extract` route calls the validator and maps validation results to existing HTTP status codes and messages.

- [X] T010 [US1] Create Pydantic response schemas for extract success and error in src/infra/schemas.py
  - **Goal**: Define response models that match existing `text`, `id`, and `format` fields and standard error payloads.
  - **Files**: src/infra/schemas.py
  - **Expected outcome**: Response models exist and describe the current API contract without changing it.

- [X] T011 [US1] Apply response models to /extract and /health routes in src/api/routes.py
  - **Goal**: Use Pydantic response models as `response_model` in FastAPI routes to validate outgoing responses.
  - **Files**: src/api/routes.py, src/infra/schemas.py
  - **Expected outcome**: Routes return data conforming to the response schemas; external JSON structure remains unchanged.

- [X] T012 [US1] Implement FastAPI dependency injection for repositories and extractors using src/api/dependencies.py and src/main.py
  - **Goal**: Move creation of `ExtractionRepository` and extractor into lifespan and inject via `Depends()` rather than manual access.
  - **Files**: src/main.py, src/api/routes.py, src/api/dependencies.py
  - **Expected outcome**: Routes receive repo and extractor via DI; no direct construction inside route functions.

- [X] T013 [US1] Remove direct usage of request.app.state in src/api/routes.py where dependencies are now injected
  - **Goal**: Ensure routes depend only on typed parameters provided by FastAPI, not on `request.app.state`.
  - **Files**: src/api/routes.py, src/api/dependencies.py
  - **Expected outcome**: `request.app.state` access is limited to dependency providers; route functions are framework-thin.

- [X] T014 [US1] Verify API contract stability against contracts/api.md via tests in tests/api/test_routes.py
  - **Goal**: Confirm paths, methods, status codes, and JSON shapes are unchanged for `/health` and `/extract`.
  - **Files**: tests/api/test_routes.py, specs/004-cv-api-refactor/contracts/api.md
  - **Expected outcome**: Tests assert that refactored routes behave identically to the documented contract.

---

## Phase 3: User Story 2 – Observability for Operations (Priority: P2) [US2]

**Goal**: Provide structured, centralized logging for upload attempts, successes, failures, and validation errors.

**Independent Test**: Trigger successful and failing uploads and confirm logs contain consistent structured entries.

- [X] T015 [US2] Integrate centralized logger into src/api/routes.py, src/services/upload_validator.py, and src/infra/extractors/*
  - **Goal**: Ensure all key operations use the shared logging configuration.
  - **Files**: src/api/routes.py, src/services/upload_validator.py, src/infra/extractors/base.py, src/infra/extractors/pdf.py, src/infra/extractors/plain_text.py
  - **Expected outcome**: Code paths for upload, validation, and extraction obtain loggers from the centralized configuration.

- [X] T016 [US2] Log upload attempts and validation outcomes in routes and validator
  - **Goal**: Emit structured log events for every upload attempt and validation error/success.
  - **Files**: src/api/routes.py, src/services/upload_validator.py
  - **Expected outcome**: Logs include fields like event type, filename, content type, size, and validation result.

- [X] T017 [US2] Log extraction successes and failures within extractor strategies and/or calling code
  - **Goal**: Capture extraction outcome, including errors from PDF parsing or text decoding.
  - **Files**: src/infra/extractors/pdf.py, src/infra/extractors/plain_text.py, src/api/routes.py
  - **Expected outcome**: Successful and failed extractions produce structured log entries without exposing sensitive data.

---

## Phase 4: User Story 3 – Large File Handling (Priority: P2) [US3]

**Goal**: Refactor file upload handling to support streaming/chunked processing and prevent large files from exhausting memory.

**Independent Test**: Upload a file near the maximum allowed size and verify successful processing with bounded memory usage.

- [X] T018 [US3] Refactor /extract route to use streaming/chunked reading from UploadFile in src/api/routes.py
  - **Goal**: Replace full `file.read()` usage with chunk iteration for upload handling.
  - **Files**: src/api/routes.py
  - **Expected outcome**: Route processes the upload via chunks, with behavior otherwise unchanged.

- [X] T019 [US3] Implement streaming-aware size checks in upload validator in src/services/upload_validator.py
  - **Goal**: Enforce `max_document_size_bytes` while reading chunks, without buffering the entire file first.
  - **Files**: src/services/upload_validator.py, src/infra/config.py
  - **Expected outcome**: Validator rejects oversized files based on streamed size calculation, preserving 413 responses.

- [X] T020 [US3] Ensure extractor strategies handle streamed or buffered content safely in src/infra/extractors/*
  - **Goal**: Adapt strategies (PDF and plain text) to accept the final buffered bytes produced by streaming logic without additional full-file reads.
  - **Files**: src/infra/extractors/base.py, src/infra/extractors/pdf.py, src/infra/extractors/plain_text.py
  - **Expected outcome**: Extractors operate correctly on data produced by streaming pipeline with no extra unbounded reads.

---

## Phase 5: User Story 4 – Maintainable and Testable Codebase (Priority: P3) [US4]

**Goal**: Achieve clear separation between routes, services, domain, and infrastructure; implement strategy pattern and improved PDF error handling; update tests for DI.

**Independent Test**: Code review and tests confirm separation, strategy usage, and testability per spec.

- [X] T021 [US4] Implement extractor strategy base and concrete strategies in src/infra/extractors/base.py, pdf.py, and plain_text.py
  - **Goal**: Replace conditional extractor logic with pluggable strategies per document type.
  - **Files**: src/infra/extractors/base.py, src/infra/extractors/pdf.py, src/infra/extractors/plain_text.py, src/domain/document_extractor_contracts.py
  - **Expected outcome**: Extractors conform to a shared interface, one per MIME type, with no centralized conditionals.

- [X] T022 [US4] Implement extractor registry to route content types to strategies in src/infra/extractors/registry.py and src/main.py
  - **Goal**: Centralize mapping of MIME constants to extractor strategies and inject this registry as the `DocumentExtractor`.
  - **Files**: src/infra/extractors/registry.py, src/main.py
  - **Expected outcome**: Registry selects the correct strategy based on MIME constants, and routes receive a single extractor entry point.

- [X] T023 [US4] Improve error handling and logging in PDF extractor in src/infra/extractors/pdf.py
  - **Goal**: Catch and log PDF parsing errors explicitly, avoiding unhandled exceptions leaking to clients.
  - **Files**: src/infra/extractors/pdf.py
  - **Expected outcome**: PDF extraction failures log error details and propagate a controlled failure for the route to map to 500 responses.

- [X] T024 [US4] Update src/api/routes.py to use strategy-based extractor and validation/service layer only
  - **Goal**: Ensure routes delegate to validator, strategy-based extractor, and repository without embedding business logic.
  - **Files**: src/api/routes.py, src/api/dependencies.py
  - **Expected outcome**: `/extract` route is thin and focused on HTTP concerns, matching the architecture plan.

- [X] T025 [US4] Refactor tests to support DI and strategy-based extractors in tests/api/test_routes.py and tests/domain/test_extractor.py
  - **Goal**: Use dependency overrides and mock strategies/repos to test routes and domain logic in isolation.
  - **Files**: tests/api/test_routes.py, tests/domain/test_extractor.py, tests/conftest.py
  - **Expected outcome**: Tests construct the app with injected dependencies and assert behavior without relying on real MongoDB or extractors.

- [X] T026 [P] [US4] Add focused tests for upload validator and extractor registry in tests/services/test_upload_validator.py and tests/infra/test_extractors/test_registry.py
  - **Goal**: Validate behavior of validation layer and registry independently from routes.
  - **Files**: tests/services/test_upload_validator.py, tests/infra/test_extractors/test_registry.py
  - **Expected outcome**: Unit tests cover edge cases for validation and strategy selection, improving overall coverage.

- [X] T027 [US4] Ensure all tests pass and adjust as needed to maintain coverage in tests/**
  - **Goal**: Run full test suite and fix any regressions from the refactor.
  - **Files**: tests/**, pyproject.toml or test configuration files
  - **Expected outcome**: `pytest` passes across all test modules; coverage is at least as high as before the refactor.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements improving maintainability, documentation, and observability without changing behavior.

- [X] T028 [P] Update quickstart and documentation to reflect new architecture in specs/004-cv-api-refactor/quickstart.md
  - **Goal**: Ensure quickstart and docs describe the final structure and usage patterns accurately.
  - **Files**: specs/004-cv-api-refactor/quickstart.md
  - **Expected outcome**: Documentation matches implemented architecture and test commands.

- [X] T029 [P] Perform targeted code cleanup and ensure logging does not leak sensitive information in src/**
  - **Goal**: Remove dead code, redundant comments, and overly verbose logging; confirm no PII in logs.
  - **Files**: src/**
  - **Expected outcome**: Code is clean, readable, and logs contain only necessary metadata.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup & Foundational**: No story-specific dependencies; must be completed before story phases.
- **Phase 2–5 (US1–US4)**: Depend on Phase 1 completion; can proceed in priority order or with limited parallelism.
- **Phase N: Polish**: Depends on completion of all required user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 1; no dependencies on other stories.
- **User Story 2 (P2)**: Depends on Phase 1; may run in parallel with US3/US4 once foundational tasks are complete.
- **User Story 3 (P2)**: Depends on Phase 1; can proceed alongside US2 as long as streaming and validation changes are coordinated.
- **User Story 4 (P3)**: Depends on Phase 1 and benefits from US1–US3 context but remains focused on internal architecture and tests.

### Parallel Opportunities

- Tasks marked [P] can be executed in parallel (different files, minimal dependencies).
- Phase 1 tasks T002 and T003 can run in parallel after T001.
- User story phases can be worked on concurrently by different developers once Phase 1 is complete, respecting shared file boundaries.

