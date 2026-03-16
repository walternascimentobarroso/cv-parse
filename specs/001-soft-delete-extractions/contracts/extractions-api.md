# Contract: Extractions API – Soft Delete, Restore, and Force Delete

## Overview

This document defines the HTTP contract additions for managing extraction lifecycle through soft delete, restore, and force delete operations.

Base path: `/extractions`

Existing GET and other non-delete endpoints are unchanged except that they will not return soft deleted records (those with `deleted_at` set).

## Common Elements

- **Path parameter**:
  - `id` (string): unique identifier of the extraction.
- **Error formats**: reuse existing error response envelope used by the API (for example, JSON body with `detail` message).

## DELETE /extractions/{id} – Soft Delete

**Description**: Marks an existing extraction as deleted without removing it from the database.

- **Request**:
  - Method: `DELETE`
  - Path: `/extractions/{id}`
  - Path params:
    - `id`: extraction identifier.
  - Body: none.

- **Behavior**:
  - If an extraction with the given `id` exists and is active (`deleted_at == null`):
    - Sets `deleted_at` to the current timestamp.
    - Sets `updated_at` to the current timestamp.
    - Logs a soft delete event.
  - If an extraction with the given `id` does not exist:
    - Returns a 404 Not Found error.
  - If an extraction with the given `id` is already soft deleted:
    - Returns a response consistent with the chosen idempotency semantics (for example, 200 OK with no changes, or a 400 error stating that it is already deleted).

- **Responses**:
  - `204 No Content` (or `200 OK` with minimal body) on successful soft delete.
  - `404 Not Found` if the extraction does not exist.
  - `400 Bad Request` if the semantics chosen for “already deleted” are error-based.

## POST /extractions/{id}/restore – Restore Soft Deleted Extraction

**Description**: Restores a previously soft deleted extraction so that it becomes active again.

- **Request**:
  - Method: `POST`
  - Path: `/extractions/{id}/restore`
  - Path params:
    - `id`: extraction identifier.
  - Body: none.

- **Behavior**:
  - If an extraction with the given `id` exists and is soft deleted (`deleted_at != null`):
    - Sets `deleted_at` to `null`.
    - Sets `updated_at` to the current timestamp.
    - Logs a restore event.
  - If an extraction with the given `id` does not exist:
    - Returns a 404 Not Found error.
  - If an extraction with the given `id` exists but is not soft deleted (`deleted_at == null`):
    - Returns a 400 Bad Request error indicating that the extraction is not deleted.

- **Responses**:
  - `200 OK` with the restored extraction representation (or a minimal confirmation body), showing `deleted_at: null` and an updated `updated_at`.
  - `404 Not Found` if the extraction does not exist.
  - `400 Bad Request` if the extraction is not currently soft deleted.

## DELETE /extractions/{id}/force – Force Delete

**Description**: Permanently removes an extraction from the database.

- **Request**:
  - Method: `DELETE`
  - Path: `/extractions/{id}/force`
  - Path params:
    - `id`: extraction identifier.
  - Body: none.

- **Behavior**:
  - If an extraction with the given `id` exists (active or soft deleted):
    - Permanently deletes the document from MongoDB.
    - Logs a force delete event.
  - If an extraction with the given `id` does not exist:
    - Returns a 404 Not Found error.

- **Responses**:
  - `204 No Content` (or `200 OK` with minimal body) on successful force delete.
  - `404 Not Found` if the extraction does not exist.

## Query Contract Changes

All default GET endpoints for extractions (single and list) MUST:

- Exclude extractions where `deleted_at` is set (soft deleted).
- Return only extractions with `deleted_at == null` by default.

No additional query parameters are introduced in this feature for including soft deleted records; this can be added later if needed as a separate extension.

