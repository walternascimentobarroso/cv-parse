# Implementation Plan: CV Extraction API Refactor

**Branch**: `004-cv-api-refactor` | **Date**: 2026-03-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-cv-api-refactor/spec.md`

## Summary

Refactor the CV extraction API to improve architecture, scalability, and maintainability while preserving the exact HTTP API contract and storage schema. The refactor introduces: named constants for collections and MIME types; dependency injection for repositories and extractors; structured, centralized logging; streaming/chunked file processing; Pydantic response models; a dedicated validation layer; domain interfaces in separate modules; and a strategy pattern for extractors. All tests are updated to match the new structure. No new extraction features or storage changes.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, motor, pdfplumber, pydantic-settings  
**Storage**: MongoDB (motor); collection and schema unchanged  
**Testing**: pytest, httpx  
**Target Platform**: Linux/server (existing)  
**Project Type**: web-service  
**Performance Goals**: Support large uploads up to configured max size without loading full file into memory; bounded memory for extraction  
**Constraints**: API contract and storage schema must remain unchanged; no new formats  
**Scale/Scope**: Existing single-service; refactor only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|--------|
| I. Single-Responsibility Modules | Pass | Routes (HTTP only), validation (rules only), domain (contracts), infra (repos, extractors) are separated. |
| II. Simplicity Over Features (YAGNI) | Pass | No new features; constants, DI, strategy, and logging are the minimum needed for the spec. |
| III. Testable, Isolated Code | Pass | DI and interfaces allow tests to inject mocks/fakes; validation and extractors are unit-testable. |
| IV. Explicit Boundaries & Dependencies | Pass | Dependencies composed at startup and injected; domain does not depend on FastAPI or MongoDB. |
| V. Consistent Style & Readability | Pass | Lint/formatter and naming conventions preserved; no new style rules. |
| Few layers | Pass | API → validation/service → domain + infra; no extra "managers" or facades. |
| Minimal dependencies | Pass | No new libraries; only structural and pattern changes. |

**Post–Phase 1**: No change; design keeps layers and dependencies minimal.

## Project Structure

### Documentation (this feature)

```text
specs/004-cv-api-refactor/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (API contract)
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by /speckit.tasks
```

### Source Code (repository root) — after refactor

```text
src/
├── api/
│   ├── __init__.py
│   ├── routes.py          # Thin: HTTP only; Depends(get_*) for repo, extractor, validator
│   └── dependencies.py   # get_repo, get_extractor, get_validator (or get_upload_service)
├── domain/
│   ├── __init__.py
│   ├── interfaces.py      # Protocol(s): DocumentExtractor, optionally ExtractionRepository
│   └── constants.py       # MIME type constants (e.g. PDF, PLAIN_TEXT)
├── services/
│   ├── __init__.py
│   ├── upload_validator.py # validate_upload(file, settings) → ValidationResult
│   └── extraction_service.py # optional orchestration: validate → extract → save (if needed)
├── infra/
│   ├── __init__.py
│   ├── config.py          # Settings; uses constants for default content types
│   ├── constants.py       # Collection names (e.g. EXTRACTIONS_COLLECTION)
│   ├── storage.py         # ExtractionRepository; uses infra constants
│   ├── schemas.py         # ExtractionRecord, response DTOs (Pydantic)
│   ├── logging_config.py  # Centralized logger factory or config
│   └── extractors/
│       ├── __init__.py
│       ├── base.py         # Strategy interface (Protocol or ABC)
│       ├── pdf.py          # PDF strategy
│       ├── plain_text.py   # Plain text strategy
│       └── registry.py    # Map content_type → strategy; used by composite/facade
└── main.py                # Lifespan: create repo, extractor registry, logger; inject into app

tests/
├── conftest.py            # Fixtures: mock repo, mock extractor, test client with overrides
├── api/
│   └── test_routes.py     # Integration: same API contract; use DI overrides
├── domain/
│   └── test_*.py          # Interfaces/constants as needed
├── services/
│   └── test_upload_validator.py
└── infra/
    └── test_extractors/   # Per-strategy and registry tests
```

**Structure Decision**: Keep existing `src/api`, `src/domain`, `src/infra`; add `src/services` for validation (and optional extraction orchestration) and `src/domain/interfaces.py` plus `src/domain/constants.py`. Extractors move under `src/infra/extractors/` with a registry to implement the strategy pattern. Constants are split: domain (MIME types) and infra (collection names) to respect boundaries. `main.py` composes all dependencies and does not rely on `request.app.state` for repo/extractor when FastAPI’s `Depends()` can supply them.

---

## Dependency Injection Approach

- **Composition root**: `main.py` (or a dedicated `composition.py`) builds: `Settings`, MongoDB client and `ExtractionRepository`, extractor registry (map of content type → strategy), upload validator, and logger. These are created once at startup inside the FastAPI lifespan.
- **Injection into routes**: Use FastAPI’s `Depends()` with provider functions (e.g. `get_repo`, `get_extractor`, `get_upload_validator`) that read from `app.state` set during lifespan. This keeps routes thin and testable; in tests, override the dependency with a test double.
- **Minimize `request.app.state` in route code**: Routes receive repo and extractor as function parameters (injected by FastAPI), not by reading `request.app.state` inside the route. `app.state` is only used in the provider functions so that the same instance is reused for all requests.
- **No global singletons**: Avoid module-level repository or extractor instances; all come from the application composition.

---

## Extractor Strategy Architecture

- **Interface**: Define a Protocol (e.g. `DocumentExtractorStrategy`) in `domain/interfaces.py`: one method, e.g. `extract(content: bytes) -> str`. Input is already validated (content type allowed and non-empty by caller).
- **Concrete strategies**: One implementation per supported type:
  - `PdfExtractor`: uses pdfplumber; reads from `io.BytesIO(content)`; catches parsing errors and logs them; returns text or raises a domain-friendly error.
  - `PlainTextExtractor`: decodes UTF-8 with errors="ignore"; returns string.
- **Registry**: A small registry (e.g. `ExtractorRegistry` or a dict) maps content type (constant) → strategy instance. The “extractor” injected into routes is this registry, which implements the same Protocol by delegating `extract(content, content_type)` to the right strategy. This removes file-type conditionals from a single place.
- **Discovery**: Registry is populated at startup in `main.py` from the list of allowed content types (so only allowed types get a strategy). No auto-discovery of new formats; adding a format remains an explicit code change (YAGNI).

---

## Validation and Service Layer Responsibilities

- **Upload validation**: Implemented in `services/upload_validator.py`. Functions (or a small class) take `UploadFile` (or equivalent) and `Settings`, and return a result type: either “ok” plus validated file metadata (and possibly stream) or “error” plus HTTP status and message. Validation checks: file present, content type in allowed list (using constants), size within limit. Size can be checked from `UploadFile` size if available, or by reading in chunks and counting (for streaming). No HTTP knowledge inside the validator (no `HTTPException`); the route translates validation errors into HTTP responses.
- **Routes**: Only HTTP: receive request, call validator, call extractor (with stream or content), call repo, return response model. If a service layer (e.g. `extraction_service`) is introduced, it orchestrates validate → extract → save and returns a result DTO; the route then maps that to the HTTP response. Keeping “orchestration” in the route is acceptable if the flow stays simple (spec: “validation in dedicated layer” is required; orchestration can stay in route or in a thin service).
- **Response models**: Pydantic models for success (e.g. `text`, `id`, `format`) and for error payloads so that responses are validated and consistent.

---

## Logging Architecture

- **Centralized setup**: One place (e.g. `infra/logging_config.py` or in `main.py`) configures the logging format (e.g. JSON or key-value) and level. All modules that log use the same format and obtain loggers via `logging.getLogger(__name__)` or a small helper that attaches the same structure (e.g. request id, feature).
- **Structured events**: Log upload attempt (e.g. filename, content type, size), extraction success (e.g. id, duration), extraction failure (e.g. error type, content type), and validation error (e.g. reason: missing file, unsupported type, size exceeded). Use consistent field names so logs are queryable.
- **Reusable**: Validation layer, extractors, and routes all use the same logging configuration; no per-module ad-hoc formatting. Logger can be injected if desired, or modules use `getLogger(__name__)` after app bootstrap has configured the root logger.

---

## Test Strategy

- **API (integration)**: `tests/api/test_routes.py` uses a test client; override FastAPI dependencies to inject in-memory or mock repo and extractor registry. Assert: same status codes, same response shape (and optionally storage side-effects) as today. No change to API contract.
- **Validation**: Unit tests for `upload_validator`: missing file, disallowed type, size over limit, valid input. Use fake `UploadFile` and `Settings`.
- **Extractors**: Unit tests per strategy (PDF, plain text) with small fixtures; test registry returns correct strategy for each type and rejects unknown type. Mock or real pdfplumber for PDF tests.
- **Repository**: Keep or add tests for `ExtractionRepository` with a real or in-memory MongoDB; ensure schema and behavior unchanged.
- **Coverage**: Maintain or improve coverage; ensure new code (validators, strategies, logging) is covered. Use dependency overrides so that tests do not depend on real DB or file system unless required.

---

## Migration Strategy for Existing Code

1. **Constants first**: Introduce `domain/constants.py` (MIME) and `infra/constants.py` (collection name). Replace magic strings in config, storage, and routes. No behavior change; tests still pass.
2. **Interfaces**: Add `domain/interfaces.py` with `DocumentExtractor` (or strategy Protocol). Make existing `SimpleDocumentExtractor` implement it; keep it in use. No behavior change.
3. **Extractors split and registry**: Implement `PdfExtractor` and `PlainTextExtractor`, and a registry that delegates by content type. Replace `SimpleDocumentExtractor` in `main.py` with the registry. Run tests; fix any regressions.
4. **Validation layer**: Move validation logic from `routes.py` into `services/upload_validator.py`. Routes call validator and map result to HTTP. Tests: route tests plus new validator unit tests.
5. **Logging**: Add logging config and log at upload, validation error, extraction success, and extraction failure. No change to responses.
6. **Streaming**: Change route to read upload in chunks (or stream) and pass stream or accumulated chunks to extractors. PDF/plain-text extractors may still need full content in memory for parsing; ensure we do not buffer the entire file in the route before validation/size check. Implement size check during streaming. Update tests for large-file behavior if needed.
7. **Response models**: Introduce Pydantic response models for success and error; use them in route return types. Ensures consistent schema.
8. **Dependency injection**: Move repo and extractor creation to lifespan; add `dependencies.py` with `get_repo`, `get_extractor` (and optionally `get_validator`) that read from `app.state`. Update routes to use `Depends(get_*)`. Remove direct `request.app.state` access from route bodies. Update tests to override these dependencies.
9. **Final pass**: Run full test suite, lint, and manual smoke test of API; confirm API contract and storage schema unchanged.

---

## Complexity Tracking

No constitution violations requiring justification. The added layers (validation, strategy extractors, constants, logging) are the minimum needed to meet the spec and constitution.
