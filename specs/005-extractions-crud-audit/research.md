# Research: CRUD and Audit Timestamps for Document Extractions

**Feature**: 005-extractions-crud-audit  
**Date**: 2026-03-15

## Resolved Decisions

### 1. Technology Stack

**Decision**: Use existing stack: FastAPI, Motor, MongoDB, Pydantic, layered (api / domain / infra).

**Rationale**: User and spec explicitly require alignment with current project structure; no new frameworks.

**Alternatives considered**: None; stack was given as constraint.

---

### 2. Soft Delete Implementation

**Decision**: Single `deleted_at` datetime field; null means active. All read queries filter `deleted_at == null` in the repository layer.

**Rationale**: Simple, auditable, allows future restore or “show deleted” without schema change. Repository encapsulates the filter so API and callers cannot accidentally expose deleted records.

**Alternatives considered**: Boolean `deleted` flag (less precise for audit); separate “archive” collection (more moving parts; out of scope).

---

### 3. Timestamp Storage and Serialization

**Decision**: Store UTC datetimes in MongoDB; serialize as ISO 8601 in API responses. Use `datetime.utcnow()` (or timezone-aware UTC) for server-set values.

**Rationale**: Matches common REST practice; avoids client timezone ambiguity. Pydantic serializes datetime to ISO 8601 by default.

**Alternatives considered**: Epoch milliseconds (less human-readable in APIs); client-provided timestamps (rejected per spec).

---

### 4. ObjectId Validation for Path Parameters

**Decision**: Validate extraction id as 24-character hex string (MongoDB ObjectId) before calling repository; return 404 for invalid format or missing/deleted record.

**Rationale**: Fails fast and avoids repository/driver errors; consistent “not found” semantics for invalid id and deleted record.

**Alternatives considered**: Let Motor raise on invalid ObjectId (leaks implementation detail); 400 for bad format and 404 for not found (both acceptable; 404 for both keeps client handling simple).

---

### 5. Update Allowed Fields

**Decision**: Define ExtractionUpdateRequest with explicitly allowed fields (e.g. `extracted_text` and any other product-defined editable fields). All audit fields (created_at, updated_at, deleted_at) and id are server-only.

**Rationale**: Spec says “allowed fields” are product-defined; minimal set is extracted text. Can extend later without changing API contract.

**Alternatives considered**: Allow partial PATCH of any non-audit field (same outcome with explicit schema); full replacement (rejected; PATCH implies partial update).

---

### 6. API Path and Backward Compatibility

**Decision**: Keep existing **POST /extract** unchanged. Add **GET /extractions**, **GET /extractions/{id}**, **PATCH /extractions/{id}**, **DELETE /extractions/{id}**.

**Rationale**: User constraint: “existing upload endpoint must continue working.” New CRUD operations live under `/extractions` for consistency.

**Alternatives considered**: Rename POST to POST /extractions (breaking change; rejected).
