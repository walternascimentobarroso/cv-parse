# Quickstart: Implementing Soft Delete in the Extractions API

This guide explains how to implement and work with soft delete, restore, and force delete for extractions in the existing FastAPI + MongoDB project.

## 1. Update the Data Model

1. Locate the extraction schema in `src/infra/schemas.py`.
2. Add or confirm the presence of:
   - `updated_at: datetime`
   - `deleted_at: Optional[datetime] = None`
3. Ensure `created_at` is already present and that all three timestamps are mapped correctly from MongoDB documents.

## 2. Update the Repository (Infra Layer)

1. Locate the extraction repository in `src/infra/storage.py` (or the appropriate infra module).
2. Implement three async methods on the repository responsible for extractions:
   - `soft_delete(id: str) -> bool` or similar result type:
     - Apply an update filter for the given id and `deleted_at == None`.
     - Set `deleted_at = now` and `updated_at = now`.
     - Return an indication of whether a document was modified.
   - `restore(id: str) -> bool`:
     - Apply an update filter for the given id and `deleted_at != None`.
     - Set `deleted_at = None` and `updated_at = now`.
     - Return an indication of whether a document was modified.
   - `force_delete(id: str) -> bool`:
     - Delete the document with the given id, regardless of its `deleted_at` value.
     - Return an indication of whether a document was deleted.
3. Centralize the default filter `deleted_at == None` in all read queries for extractions so that soft deleted documents are not returned by default.

## 3. Wire API Endpoints (API Layer)

1. In `src/api/routes.py`, add or update routes:
   - `DELETE /extractions/{id}` → calls `repository.soft_delete`.
   - `POST /extractions/{id}/restore` → calls `repository.restore`.
   - `DELETE /extractions/{id}/force` → calls `repository.force_delete`.
2. For each route:
   - If the repository method indicates “no document found”, raise an HTTP 404.
   - For restore, if the repository method indicates “not in deleted state”, raise a 400 error with a clear message.
   - On success, return `204 No Content` (or `200 OK` with a minimal body) according to the contract.

## 4. Manage Timestamps

Ensure that all write operations for extractions keep timestamps consistent:

- On creation:
  - `created_at = now`
  - `updated_at = now`
  - `deleted_at = None`
- On soft delete:
  - `deleted_at = now`
  - `updated_at = now`
- On restore:
  - `deleted_at = None`
  - `updated_at = now`

Use a single helper (for example, a function that returns the current timezone-aware datetime) to avoid duplication.

## 5. Logging

1. Use the existing logger configuration in `src/infra/logging_config.py`.
2. Log at INFO level for:
   - Soft delete: include extraction id and timestamp.
   - Restore: include extraction id and timestamp.
   - Force delete: include extraction id and timestamp.
3. Avoid logging full extraction contents or sensitive data.

## 6. Tests

1. Create or update repository tests (for example, `tests/infra/test_extraction_repository.py`) to cover:
   - Soft delete updates `deleted_at` and `updated_at` and excludes the record from default queries.
   - Restore clears `deleted_at`, updates `updated_at`, and makes the record visible again.
   - Force delete removes the record.
2. Create or update API tests (for example, `tests/api/test_extractions_soft_delete.py`) to cover:
   - Successful soft delete, restore, and force delete HTTP flows.
   - 404 behavior when the id does not exist.
   - 400 behavior when attempting to restore a non-deleted record.

Following these steps will implement the soft delete behavior in a way that aligns with the project’s DDD structure and existing technology choices.

