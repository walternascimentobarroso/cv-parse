# Quickstart: CRUD and Audit Timestamps (005-extractions-crud-audit)

**Feature**: 005-extractions-crud-audit  
**Date**: 2026-03-15

## Prerequisites

- Python 3.12, uv (or project tooling)
- MongoDB running (e.g. Docker: `docker run -d -p 27017:27017 mongo`)
- Environment: `.env` or env vars for `MONGODB_URI`, `MONGODB_DB`, etc., per project config.

## Install and run

```bash
# From repository root
make install   # or: uv sync
make run       # or: uv run uvicorn src.main:app --reload
```

API base URL: `http://localhost:8000` (or as configured).

## Verify behavior

1. **Create extraction** (existing flow):  
   `POST /extract` with a PDF/form-data file. Note the returned `id`.

2. **List extractions**:  
   `GET /extractions` — response is a JSON array; each item includes `created_at`, `updated_at` (null until first update).

3. **Get one**:  
   `GET /extractions/{id}` — use id from step 1. Expect 200 with full detail including timestamps.

4. **Update**:  
   `PATCH /extractions/{id}` with body e.g. `{ "extracted_text": "Updated text" }`. Expect 200; `updated_at` should be set.

5. **Soft delete**:  
   `DELETE /extractions/{id}`. Expect 204. Then `GET /extractions/{id}` and `GET /extractions` should no longer return that record (404 and list without it).

6. **Idempotent delete**:  
   `DELETE /extractions/{id}` again — expect 404.

## Tests

```bash
make test        # or: uv run pytest tests/
uv run pytest tests/api/   # API route tests
uv run pytest tests/infra/ # Repository and schema tests
```

## Implementation order (for developers)

1. Schema: Add `updated_at`, `deleted_at` to `ExtractionRecord`; add response and update-request Pydantic models.
2. Repository: Implement `find_by_id`, `find_all`, `update`, `soft_delete` with `deleted_at == null` filter; ensure `save_extraction` sets all three timestamps.
3. Routes: Add GET /extractions, GET /extractions/{id}, PATCH /extractions/{id}, DELETE /extractions/{id}; keep POST /extract unchanged.
4. Validation: ObjectId validation for id; PATCH body restricted to allowed fields.
5. Tests: Unit tests for repository and schema; API tests for each endpoint and 404/422 cases.
