# Research: Soft Delete and Restore for Extractions

## Overview

This feature extends the existing Extractions API (FastAPI + MongoDB + Motor) to support soft delete, restore, and force delete behavior without changing the underlying technology stack or architectural style.

The specification does not introduce open technical unknowns that require additional research beyond standard best practices for:

- Timestamp fields (`created_at`, `updated_at`, `deleted_at`) in MongoDB documents.
- Soft delete patterns with MongoDB + Motor.
- FastAPI route design and error handling.

Because the stack and patterns are already established in the project, all prior “NEEDS CLARIFICATION” placeholders can be resolved using existing conventions.

## Decisions

### 1. Soft Delete Representation

- **Decision**: Represent soft delete state with a nullable `deleted_at` field on the extraction document and Pydantic schema.
- **Rationale**: Timestamp-based soft delete is a standard pattern with MongoDB; it allows auditing when a delete occurred and keeps the implementation simple.
- **Alternatives considered**:
  - Boolean `is_deleted` flag: rejected because it loses deletion time information and does not add meaningful simplicity.
  - Separate “trash” collection: rejected as overkill for current scope and would complicate queries and references.

### 2. Timestamp Management

- **Decision**: Maintain both `created_at` and `updated_at` on the extraction, and set or clear `deleted_at` as follows:
  - Soft delete: `deleted_at = now`, `updated_at = now`.
  - Restore: `deleted_at = null`, `updated_at = now`.
  - Force delete: document removed from MongoDB, no timestamp updates.
- **Rationale**: Keeping `updated_at` in sync with state-changing operations aligns with auditing needs and makes it easy to see recent changes.
- **Alternatives considered**:
  - Only using `deleted_at` without `updated_at`: rejected because other non-delete updates may already exist or future features may rely on `updated_at`.

### 3. Query Behavior

- **Decision**: Apply a default filter `deleted_at == null` to all repository read queries that back public GET endpoints.
- **Rationale**: Centralizing the filter in the repository enforces consistent behavior across all callers and respects the DDD separation (infra owns data access semantics).
- **Alternatives considered**:
  - Filtering in API routes: rejected because it would duplicate logic across handlers and couple behavior to the transport layer.
  - Allowing clients to control inclusion of soft deleted items: out of scope for this feature and could complicate the API contract prematurely.

### 4. Error Handling Strategy

- **Decision**:
  - If an extraction id does not exist for any of the three operations, return HTTP 404 (not found).
  - For restore when the extraction exists but `deleted_at` is null, return HTTP 400 (bad request) with a clear message (e.g., “Extraction is not deleted”).
- **Rationale**: Distinguishes “resource missing” from “invalid state for requested operation” while keeping behavior predictable for clients.
- **Alternatives considered**:
  - Returning 404 for “not deleted” restore: rejected because it hides the resource’s existence and can be misleading.

### 5. Logging

- **Decision**: Log at INFO level for soft delete, restore, and force delete operations, including the extraction id (and possibly correlation/request id if available).
- **Rationale**: Provides traceability for destructive operations without exposing sensitive data; aligns with existing `logging_config.py` conventions.
- **Alternatives considered**:
  - No additional logging: rejected because soft/force delete and restore are operationally significant.

## Result

All specification requirements can be implemented using existing technologies and patterns. No further research tasks are required before proceeding to the detailed design in `data-model.md`, contracts, and quickstart documentation.

