# Implementation Plan: CRUD and Audit Timestamps for Document Extractions

**Branch**: `005-extractions-crud-audit` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/005-extractions-crud-audit/spec.md`

## Summary

Extend the existing FastAPI CV extraction service with full CRUD over extraction records, server-set audit timestamps (`created_at`, `updated_at`, `deleted_at`), and soft delete. The repository layer will automatically exclude soft-deleted records from all reads; routes remain async and use Pydantic response models. The current POST `/extract` upload flow is preserved.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Motor (async MongoDB), Pydantic  
**Storage**: MongoDB (Motor async driver)  
**Testing**: pytest, httpx  
**Target Platform**: Linux/server (Docker-friendly)  
**Project Type**: web-service (REST API)  
**Performance Goals**: Async I/O; no blocking in request path  
**Constraints**: Repository must filter `deleted_at == null` on all reads; routes async; responses via Pydantic schemas; existing upload endpoint unchanged  
**Scale/Scope**: Single service; no pagination in this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|--------|
| I. Single-Responsibility Modules | Pass | API routes delegate to services/repo; domain stays pure; infra owns persistence and schemas |
| II. Simplicity Over Features (YAGNI) | Pass | CRUD + timestamps + soft delete only; no auth, no permanent delete, no pagination |
| III. Testable, Isolated Code | Pass | Repository and routes use DI; business rules testable without DB |
| IV. Explicit Boundaries & Dependencies | Pass | api → domain contracts / services; infra → storage, schemas; no framework in domain |
| V. Consistent Style & Readability | Pass | Existing ruff/lint; descriptive names; no dead code |

## Project Structure

### Documentation (this feature)

```text
specs/005-extractions-crud-audit/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (API contract)
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── dependencies.py   # get_repo, get_extractor (unchanged)
│   └── routes.py        # Add GET/PATCH/DELETE /extractions, keep POST /extract
├── domain/
│   └── (extractor contracts; no new domain entities)
├── infra/
│   ├── config.py
│   ├── schemas.py       # ExtractionRecord + new response models
│   └── storage.py      # ExtractionRepository: save, find_by_id, find_all, update, soft_delete
├── services/
│   └── upload_validator.py
└── main.py

tests/
├── api/
├── domain/
└── infra/
```

**Structure Decision**: Layered layout (api / domain / infra) is preserved. CRUD and timestamp logic live in infra (repository + schemas) and api (routes); domain remains focused on extraction contracts.

## Step-by-Step Technical Plan

### 1. Schema changes

- **ExtractionRecord** (infra): Add `updated_at: datetime | None = None`, `deleted_at: datetime | None = None`. Keep `created_at` (already present). All three are server-set only; do not allow client input for these fields.
- **Pydantic response models** (infra/schemas.py):
  - **ExtractionCreateResponse**: id, text, format (current POST /extract response shape; can alias or keep as `ExtractResponse` for backward compatibility).
  - **ExtractionDetailResponse**: id, filename, content_type, size_bytes, extracted_text, status, created_at, updated_at (no deleted_at in response).
  - **ExtractionListResponse**: list of items with same shape as detail (id, filename, content_type, size_bytes, extracted_text, status, created_at, updated_at).
  - **ExtractionUpdateResponse**: same as ExtractionDetailResponse (return full record after PATCH).
- **Update payload**: Define **ExtractionUpdateRequest** with only allowed updatable fields (e.g. `extracted_text`, or other product-defined fields); exclude id, created_at, updated_at, deleted_at.

### 2. Repository changes

- **ExtractionRepository** (infra/storage.py):
  - **save_extraction** (existing): Set `created_at = datetime.utcnow()`, `updated_at = None`, `deleted_at = None` on insert. Return str(id).
  - **find_by_id(id: str)**: Query by `_id` and `deleted_at: None`. Return single document or None. Use ObjectId(id) with invalid-id handling (return None or raise consistent with project).
  - **find_all()**: Query with `deleted_at: None`. Return list of records (cursor to list).
  - **update(id: str, payload: dict)**: Ensure `deleted_at` is null and document exists; set `updated_at = datetime.utcnow()`; apply only allowed fields from payload; do not allow overwriting `created_at`, `deleted_at`, or `_id`. Return updated document or None if not found.
  - **soft_delete(id: str)**: Set `deleted_at = datetime.utcnow()` where `deleted_at` is null. Return True if a document was modified, False otherwise.
- All read methods must use a shared filter: `deleted_at == null` (e.g. `{"deleted_at": None}`). Optionally add a small helper to build the “active” filter to avoid duplication.

### 3. API route changes

- **POST /extract** (existing): Unchanged. Continues to call `repo.save_extraction(...)` (which will set created_at/updated_at/deleted_at). Response remains ExtractResponse (or ExtractionCreateResponse alias).
- **GET /extractions**: New. Async. Depends on repo. Call `repo.find_all()`, map to list of ExtractionDetailResponse (or ExtractionListResponse wrapping that list). Return 200 with list.
- **GET /extractions/{id}**: New. Async. Depends on repo. Call `repo.find_by_id(id)`. If None, return 404. Else return ExtractionDetailResponse.
- **PATCH /extractions/{id}**: New. Async. Depends on repo. Validate body with ExtractionUpdateRequest. Call `repo.update(id, payload)`. If None, return 404. Else return ExtractionUpdateResponse (same shape as detail).
- **DELETE /extractions/{id}**: New. Async. Depends on repo. Call `repo.soft_delete(id)`. If False, return 404. If True, return 204 No Content (or 200 with minimal body per team convention).
- All routes remain async; use `Annotated[ExtractionRepository, Depends(get_repo)]` (or equivalent) for DI.

### 4. Validation rules

- **Existing upload validation**: Unchanged (file type, size, etc.) for POST /extract.
- **GET/PATCH/DELETE by id**: Validate id is a valid 24-char hex ObjectId (or reject early with 404/400). Do not allow operations on soft-deleted records: repository already excludes them in find_by_id and update/soft_delete semantics.
- **PATCH body**: Only allowed fields in ExtractionUpdateRequest; reject unknown or forbidden fields (e.g. id, created_at, updated_at, deleted_at). Return 422 for invalid body.
- **Business rules**: (1) Record must exist and not be soft-deleted for update and soft_delete. (2) Soft-deleted records must not be returned by GET list or GET by id. Enforce via repository API (repository returns None for missing or deleted).

### 5. Timestamp handling

- **created_at**: Set once in `save_extraction` at insert using `datetime.utcnow()` (or timezone-aware now if project standard is UTC).
- **updated_at**: Set in repository `update` method to current time on every successful update; leave null until first update. Do not set on insert (or set null on insert).
- **deleted_at**: Set in repository `soft_delete` to current time; null until soft-deleted.
- Store in MongoDB as datetime; serialize in Pydantic responses as ISO 8601. Do not accept these fields from the client in create or update.

### 6. Soft delete strategy

- **Persistence**: Records remain in the same collection; no physical delete. `deleted_at` is the only flag.
- **Reads**: All read paths (find_by_id, find_all) include filter `deleted_at == null`. No “include deleted” in scope.
- **Writes**: Update and soft_delete must only affect documents where `deleted_at` is null. Soft delete is implemented as an update setting `deleted_at` to now.
- **Idempotence**: Soft-deleting an already soft-deleted id returns “not found” (repository returns False; route returns 404). No permanent delete or restore in this feature.

## Complexity Tracking

*(No constitution violations; this section left empty.)*
