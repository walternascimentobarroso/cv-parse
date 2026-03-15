# Data Model: Extraction Record (005-extractions-crud-audit)

**Feature**: CRUD and Audit Timestamps  
**Date**: 2026-03-15

## Entity: Extraction Record

Stored in MongoDB in the existing extractions collection. Represents one document extraction (upload → extract text → persist).

### Attributes

| Field | Type | Required | Set By | Notes |
|-------|------|----------|--------|--------|
| _id | ObjectId | Yes | Server | MongoDB primary key; exposed as string id in API |
| filename | string \| null | Yes | Server | Original filename from upload |
| content_type | string | Yes | Server | MIME type (e.g. application/pdf) |
| size_bytes | integer | Yes | Server | File size in bytes |
| extracted_text | string | Yes | Server / Client (on update) | Extracted text content |
| status | string | Yes | Server | e.g. "success" |
| created_at | datetime | Yes | Server | Set once on insert; UTC |
| updated_at | datetime \| null | No | Server | Null until first update; then set on each update; UTC |
| deleted_at | datetime \| null | No | Server | Null while active; set on soft delete; UTC |

### Validation Rules

- **created_at**: Must be set on insert; never updated by client or by update/soft_delete.
- **updated_at**: Must be null on insert; set by server on every successful PATCH; client cannot send.
- **deleted_at**: Must be null on insert and on update; set by server only in soft_delete; client cannot send.
- **id** (API): 24-character hex string when used in path/query (ObjectId string representation).
- **extracted_text** (and any other updatable fields): Validated by ExtractionUpdateRequest in API layer.

### State Transitions

1. **Created**: Document inserted with `created_at` set, `updated_at` and `deleted_at` null.
2. **Updated**: One or more PATCH operations set `updated_at` to current time; `deleted_at` remains null.
3. **Soft deleted**: DELETE sets `deleted_at` to current time. Record is excluded from all normal reads (find_by_id, find_all).

No transition from soft-deleted back to active in this feature (no restore).

### Relationships

- None. Extraction is a standalone document; no references to users or other collections in scope.

### Indexes (recommended for implementation)

- `_id` (default).
- Optional: `deleted_at` (e.g. `{ "deleted_at": 1 }`) to optimize “active only” queries. Not required for correctness.
