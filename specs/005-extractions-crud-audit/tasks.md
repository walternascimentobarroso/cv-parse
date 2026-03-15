# Tasks: CRUD and Audit Timestamps for Document Extractions

**Feature Branch**: `005-extractions-crud-audit`  
**Input**: plan.md, spec.md, data-model.md, contracts/extractions-api.md  
**Structure**: src/api, src/domain, src/infra

Tasks are grouped by **Schema**, **Repository**, **API**, **Validation**, and **Testing**. Each task is atomic, one-commit, with no code—description and files only. Execution order respects dependencies (Schema → Repository → API → Validation → Testing).

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Parallelizable (different files or independent changes).
- **[US1/US2/US3]**: Maps to User Story 1 (Create & Retrieve), 2 (List & Update), 3 (Soft Delete).
- Every task includes the file path(s) affected.

---

## Schema

- [x] T001 [P] Add `updated_at` and `deleted_at` to ExtractionRecord in src/infra/schemas.py

**T001 — Audit fields on ExtractionRecord**  
**Description**: Add two optional datetime fields to ExtractionRecord: `updated_at` and `deleted_at`, both defaulting to None. Keep `created_at` as-is. Ensure serialization (e.g. model_dump / to_mongo) includes them so new documents are stored with all three audit fields.  
**Files affected**: src/infra/schemas.py

---

- [x] T002 [P] Add ExtractionDetailResponse and list shape in src/infra/schemas.py

**T002 — Detail and list response models**  
**Description**: Define Pydantic models for API responses: ExtractionDetailResponse (id, filename, content_type, size_bytes, extracted_text, status, created_at, updated_at; no deleted_at). Define the list response as a list of the same detail shape (or ExtractionListResponse wrapping it).  
**Files affected**: src/infra/schemas.py

---

- [x] T003 [P] Add ExtractionUpdateRequest and ExtractionUpdateResponse in src/infra/schemas.py

**T003 — Update request and response models**  
**Description**: Define ExtractionUpdateRequest with only allowed updatable fields (e.g. extracted_text); exclude id and all audit fields. Define ExtractionUpdateResponse with the same shape as ExtractionDetailResponse for PATCH responses.  
**Files affected**: src/infra/schemas.py

---

## Repository

- [x] T004 Add shared active filter (deleted_at is null) in src/infra/storage.py

**T004 — Active filter for reads**  
**Description**: Introduce a single place (e.g. helper or constant) that builds the filter for “active” documents: deleted_at is null. Use this in all read and write operations that must target only non–soft-deleted records so behavior stays consistent and soft-deleted records never leak.  
**Files affected**: src/infra/storage.py

---

- [x] T005 Update save_extraction to set updated_at and deleted_at to null in src/infra/storage.py

**T005 — Timestamps on insert**  
**Description**: In save_extraction, when building the ExtractionRecord (or the document for insert), set updated_at and deleted_at to None in addition to created_at. Ensure the inserted document contains all three audit fields so new records match the data model.  
**Files affected**: src/infra/storage.py

---

- [x] T006 [US1] Implement find_by_id with active filter in src/infra/storage.py

**T006 — Find extraction by id**  
**Description**: Add find_by_id(id: str) that queries by _id (ObjectId) and the active filter (deleted_at null). Return the document or None. Handle invalid ObjectId (e.g. bad length or non-hex) by returning None or following project convention so callers get a single “not found” outcome.  
**Files affected**: src/infra/storage.py

---

- [x] T007 [US2] Implement find_all with active filter in src/infra/storage.py

**T007 — List active extractions**  
**Description**: Add find_all() that queries the collection with the active filter (deleted_at null), and returns a list of documents (e.g. cursor to list). No pagination in this feature.  
**Files affected**: src/infra/storage.py

---

- [x] T008 [US2] Implement update with updated_at and active filter in src/infra/storage.py

**T008 — Update extraction**  
**Description**: Add update(id: str, payload: dict) that updates only documents matching _id and the active filter. Set updated_at to current UTC time; apply only allowed fields from payload; do not overwrite _id, created_at, or deleted_at. Return the updated document or None if no document was updated.  
**Files affected**: src/infra/storage.py

---

- [x] T009 [US3] Implement soft_delete in src/infra/storage.py

**T009 — Soft delete extraction**  
**Description**: Add soft_delete(id: str) that sets deleted_at to current UTC for documents matching _id and where deleted_at is null. Do not remove the document. Return True if one document was updated, False otherwise (id not found or already soft-deleted).  
**Files affected**: src/infra/storage.py

---

## API

- [x] T010 [US1] Add GET /extractions/{id} route in src/api/routes.py

**T010 — Get extraction by id**  
**Description**: Add an async GET route for /extractions/{id}. Use repo.find_by_id(id). If result is None, return 404. Otherwise return 200 with body shaped as ExtractionDetailResponse (id, filename, content_type, size_bytes, extracted_text, status, created_at, updated_at). Use Depends(get_repo) for the repository.  
**Files affected**: src/api/routes.py

---

- [x] T011 [US2] Add GET /extractions list route in src/api/routes.py

**T011 — List extractions**  
**Description**: Add an async GET route for /extractions. Call repo.find_all(), map each document to ExtractionDetailResponse (or the list response model), and return 200 with the list. No pagination.  
**Files affected**: src/api/routes.py

---

- [x] T012 [US2] Add PATCH /extractions/{id} route in src/api/routes.py

**T012 — Update extraction**  
**Description**: Add an async PATCH route for /extractions/{id}. Accept body as ExtractionUpdateRequest. Call repo.update(id, payload). If result is None, return 404. Otherwise return 200 with ExtractionUpdateResponse (same shape as detail).  
**Files affected**: src/api/routes.py

---

- [x] T013 [US3] Add DELETE /extractions/{id} route in src/api/routes.py

**T013 — Soft delete extraction**  
**Description**: Add an async DELETE route for /extractions/{id}. Call repo.soft_delete(id). If False, return 404. If True, return 204 No Content (or agreed convention). Do not remove the document from the database.  
**Files affected**: src/api/routes.py

---

## Validation

- [x] T014 Add ObjectId validation for extraction id path parameter

**T014 — Validate id format**  
**Description**: For GET /extractions/{id}, PATCH /extractions/{id}, and DELETE /extractions/{id}, validate that id is a valid 24-character hex string (MongoDB ObjectId) before calling the repository. If invalid, return 404 (or 400) so that invalid id and missing/deleted record are handled consistently. Implement in routes or a shared validator used by routes.  
**Files affected**: src/api/routes.py (and optionally a small helper in src/api/ or src/infra/)

---

- [x] T015 Ensure PATCH body validated with ExtractionUpdateRequest only

**T015 — PATCH body validation**  
**Description**: Ensure the PATCH /extractions/{id} body is validated with ExtractionUpdateRequest so that only allowed fields are accepted. Reject requests that include id, created_at, updated_at, or deleted_at with 422. No server-set audit fields from client input.  
**Files affected**: src/api/routes.py

---

## Testing

- [x] T016 Add repository unit tests for find_by_id, find_all, update, soft_delete in tests/infra/

**T016 — Repository tests**  
**Description**: Add tests that cover ExtractionRepository: find_by_id (found, not found, invalid id, soft-deleted excluded); find_all (only active records); update (success, not found, soft-deleted excluded, updated_at set); soft_delete (success, idempotent second call returns False). Use in-memory or test DB as per project practice.  
**Files affected**: tests/infra/ (e.g. tests/infra/test_storage.py or equivalent)

---

- [x] T017 Add API tests for GET /extractions, GET /extractions/{id}, PATCH, DELETE in tests/api/

**T017 — API route tests**  
**Description**: Add tests for the new routes: GET /extractions (list, only active); GET /extractions/{id} (200 with body, 404 for missing/invalid/soft-deleted); PATCH (200 with updated body, 404, 422 for invalid body); DELETE (204, 404 for missing or already soft-deleted). Use TestClient/httpx and optionally test DB or mocks.  
**Files affected**: tests/api/ (e.g. tests/api/test_routes.py or equivalent)

---

## Dependencies and execution order

- **Schema (T001–T003)**: No dependency on other tasks; T002/T003 can run in parallel after T001 if desired. All schema tasks must be done before repository tasks that persist or return the new fields.
- **Repository (T004–T009)**: T004 first (active filter). T005 (save_extraction) next. T006–T009 depend on T004; T007, T008, T009 can be implemented in any order after T004 and T005.
- **API (T010–T013)**: Depend on repository methods and response/request models. T010 after T006; T011 after T007; T012 after T008; T013 after T009.
- **Validation (T014–T015)**: T014 can be done with or right after the routes that use id. T015 is satisfied by using ExtractionUpdateRequest in PATCH (can be part of T012 or a separate pass).
- **Testing (T016–T017)**: After the code under test exists; T016 after T004–T009, T017 after T010–T015.

**Suggested commit order**: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017. Parallel: T002/T003; T006/T007; T008/T009; T010–T013 (after repo ready); T016/T017.

---

## Summary

| Category   | Task IDs   | Count |
|-----------|------------|-------|
| Schema    | T001–T003  | 3     |
| Repository| T004–T009  | 6     |
| API       | T010–T013  | 4     |
| Validation| T014–T015  | 2     |
| Testing   | T016–T017  | 2     |
| **Total** |            | **17**|

**MVP scope (User Story 1)**: T001–T006, T010, T014 (schema, repository with find_by_id, GET by id, id validation).  
**Full CRUD**: All tasks T001–T015.  
**With tests**: T016–T017.
