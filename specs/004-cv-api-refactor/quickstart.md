# Quickstart: Working with the Refactored CV Extraction API

This guide describes how to run, test, and extend the codebase after the 004-cv-api-refactor.

---

## Prerequisites

- Python 3.12
- MongoDB (e.g. local or `mongodb://mongodb:27017`)
- `uv` (or project’s chosen environment manager); see repo root for install steps.

---

## Install and run

```bash
make install   # or: uv sync
# Start MongoDB if not already running
uv run uvicorn src.main:app --reload
```

- Health: `GET http://localhost:8000/health`
- Extract: `POST http://localhost:8000/extract` with multipart form body, file key as in current API (e.g. `file`).

---

## Project layout (after refactor)

- **`src/api/`**: HTTP only. Routes use `Depends(get_repo)` and `Depends(get_extractor)` from `api/dependencies.py`; validation is done via `services.upload_validator.validate_upload`. No business logic in routes; response models in `infra/schemas.py`.
- **`src/domain/`**: Contract protocols (e.g. `DocumentExtractor`) in `document_extractor_contracts.py`; MIME/content-type constants in `constants.py`. No FastAPI, no MongoDB.
- **`src/services/`**: Upload validation in `upload_validator.py` (result type: `ValidationOk` | `ValidationError`). Pure functions; no HTTP.
- **`src/infra/`**: Config, MongoDB repository, schemas (`ExtractionRecord`, `ExtractResponse`, `HealthResponse`), logging config, and extractors (base, pdf, plain_text, registry). Uses domain constants and contracts.

Dependencies are created in `main.py` lifespan and injected via FastAPI’s dependency system.

---

## Adding a new extraction format

1. Add a new MIME constant in `src/domain/constants.py` if needed.
2. Implement a strategy in `src/infra/extractors/` that satisfies the extractor Protocol (e.g. `extract(content: bytes) -> str`).
3. Register the strategy in the extractor registry in `main.py` (or in the registry module) for that content type.
4. Add the content type to allowed types in config (already using constants).
5. Add unit tests for the new strategy and update API tests if the contract changes (this refactor does not add new formats).

---

## Testing

- **All tests**: `uv run pytest tests/` or `make test`
- **By layer**: `uv run pytest tests/api/`, `tests/services/`, `tests/infra/`, `tests/domain/`
- **Override dependencies**: In tests, use FastAPI’s `app.dependency_overrides` to inject mock repo and extractor so API tests do not require a real MongoDB.

---

## Logging

Logging is configured once (e.g. in `infra/logging_config.py` or at app startup). Use `logging.getLogger(__name__)` in routes, validators, and extractors. Emit structured events for: upload attempt, validation error, extraction success, extraction failure (with error details). Do not log full file content or PII.

---

## Constants

- **Collections**: Use the constant from `infra/constants.py` (e.g. `EXTRACTIONS_COLLECTION`) when referring to the extraction collection.
- **MIME types**: Use constants from `domain/constants.py` (e.g. for PDF, plain text) in validation and config. Do not use magic strings in route or domain logic.

---

## API contract

See `specs/004-cv-api-refactor/contracts/api.md`. The refactor does not change the API contract; only internal architecture and structure change.
