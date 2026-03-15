# Feature Specification: CRUD and Audit Timestamps for Document Extractions

**Feature Branch**: `005-extractions-crud-audit`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Feature: CRUD endpoints and audit timestamps for document extractions…"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Retrieve Extraction (Priority: P1)

A user uploads a document and receives a new extraction record. They can later retrieve that record by its identifier to view the extracted text and metadata.

**Why this priority**: Creation and read-by-id are the foundation; without them no other operations apply.

**Independent Test**: Upload a document, receive a created record with a unique identifier and timestamps; request that record by id and receive the same data. Deleted records are not returned.

**Acceptance Scenarios**:

1. **Given** no prior extraction, **When** the user uploads a document and extraction completes, **Then** a new record is stored with a unique id, extracted text, and `created_at` set to the current time.
2. **Given** an existing non-deleted extraction with id X, **When** the user requests the extraction by id X, **Then** the system returns the full record including `created_at` and `updated_at`.
3. **Given** an extraction that has been soft deleted, **When** the user requests it by id, **Then** the system responds as if the record does not exist (e.g. 404).

---

### User Story 2 - List and Update Extractions (Priority: P2)

A user lists all extraction records to see what has been processed, and can update an existing record (e.g. correct or enrich extracted data). The system tracks when each record was last modified.

**Why this priority**: List and update complete the core CRUD workflow for day-to-day use.

**Independent Test**: Create several extractions, list them and confirm only non-deleted records appear; update one record and confirm `updated_at` changes and the record is returned correctly.

**Acceptance Scenarios**:

1. **Given** multiple extraction records (some possibly soft deleted), **When** the user requests the list of extractions, **Then** the system returns only records where `deleted_at` is null, with `created_at` and `updated_at` present.
2. **Given** an existing non-deleted extraction, **When** the user submits an update for allowed fields, **Then** the record is updated and `updated_at` is set to the current time; `created_at` is unchanged.
3. **Given** an extraction that has been soft deleted, **When** the user attempts to update it, **Then** the system rejects the request (e.g. 404 or 410).

---

### User Story 3 - Soft Delete Extraction (Priority: P3)

A user can “delete” an extraction so it no longer appears in lists or read-by-id, without physically removing data. The record remains stored with a deletion timestamp for audit or recovery.

**Why this priority**: Soft delete supports compliance and undo scenarios without complicating normal reads.

**Independent Test**: Create an extraction, soft delete it, then confirm it does not appear in list or get-by-id; the record still exists in storage with `deleted_at` set.

**Acceptance Scenarios**:

1. **Given** an existing non-deleted extraction, **When** the user requests soft delete, **Then** the system sets `deleted_at` to the current time and does not remove the document from storage.
2. **Given** a soft deleted extraction, **When** the user lists extractions or requests it by id, **Then** the record is excluded from results.
3. **Given** a non-existent or already soft deleted extraction id, **When** the user requests soft delete, **Then** the system responds with an error (e.g. 404).

---

### Edge Cases

- Requesting an extraction by an id that does not exist or is soft deleted: system returns a clear “not found” style response.
- Updating a record that does not exist or is soft deleted: system rejects the operation and does not create a new record.
- Soft deleting an already soft deleted record: system treats it as “not found” and does not change `deleted_at` again.
- List returns only non-deleted records; no special “include deleted” option in scope for this feature.
- Timestamps are set by the server at the time of the operation; client-provided timestamps for audit fields are not accepted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support creating an extraction record when a document is uploaded (upload, extract text, save) and set `created_at` at creation time.
- **FR-002**: The system MUST support reading a single extraction by identifier; records with non-null `deleted_at` MUST NOT be returned (treated as not found).
- **FR-003**: The system MUST support listing extraction records; the list MUST exclude any record where `deleted_at` is not null.
- **FR-004**: The system MUST support updating an extraction by identifier for allowed fields; the system MUST set `updated_at` to the current time on each successful update and MUST NOT return or update records that are soft deleted.
- **FR-005**: The system MUST support soft delete: setting `deleted_at` to the current timestamp for a record identified by id, without removing the record from storage; soft deleted records MUST NOT appear in list or read-by-id.
- **FR-006**: Every extraction record MUST have `created_at` (set once at creation); `updated_at` (null until first update, then set on each update); `deleted_at` (null until soft deleted, then set to deletion time).
- **FR-007**: The system MUST validate that a record exists and is not soft deleted before allowing update or soft delete; otherwise return an appropriate error (e.g. not found).
- **FR-008**: The system MUST expose response shapes for: creation result, single extraction detail, list of extractions, and update result (structure and fields appropriate for each operation).

### Key Entities

- **Extraction record**: A stored result of document processing. Key attributes: unique identifier, extracted text (and any existing metadata), `created_at`, `updated_at`, `deleted_at`. Lifecycle: created → optionally updated → optionally soft deleted. Soft deleted records are excluded from normal read and list.
- **Audit timestamps**: `created_at` (required, set on insert), `updated_at` (optional until first update), `deleted_at` (optional until soft delete). All are server-set; no client override.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create an extraction by uploading a document and receive a persisted record with `created_at` and a stable identifier.
- **SC-002**: Users can retrieve a non-deleted extraction by id and see correct `created_at` and `updated_at`; soft deleted records are not returned.
- **SC-003**: Users can list all non-deleted extractions; the list excludes soft deleted records and includes timestamp fields.
- **SC-004**: Users can update a non-deleted extraction and see `updated_at` change on the next read; soft deleted or missing records cannot be updated.
- **SC-005**: Users can soft delete an extraction; the record no longer appears in list or get-by-id, and `deleted_at` is set.
- **SC-006**: All create/read/list/update/soft-delete behaviors align with the existing layered structure (api / domain / infra) and keep persistence and API boundaries clear.

## Assumptions

- The existing “create on upload” flow remains the only way to create an extraction; no separate “create empty record” endpoint is required.
- “Allowed fields” for update are defined by the current product rules (e.g. extracted text or metadata); the exact set is defined in implementation within the scope of this feature.
- No authentication or user context; operations are applied to extraction records without user attribution.
- No permanent delete or purge endpoint; no pagination for list in this feature.
- Read and list queries always filter out soft deleted records; no “show deleted” option in scope.

## Non-Goals

- Authentication or user tracking.
- Permanent delete endpoint.
- Pagination for list endpoint.
- “Include deleted” or restore-deleted in this feature.
