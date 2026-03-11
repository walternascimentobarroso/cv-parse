# Data Model: Doc-to-Text API

**Feature**: 001-doc-to-text-api  
**Date**: 2026-03-10

## Overview

Data is stored in MongoDB. The only persisted entity is the **extraction record**, representing one document submission and its extracted text (and metadata). No separate “document binary” collection in v1 to keep storage minimal.

## Entities

### ExtractionRecord (MongoDB document)

Represents one document processing request and its result. Stored in a single collection (e.g. `extractions`).

| Field           | Type     | Description |
|----------------|----------|-------------|
| `_id`          | ObjectId | MongoDB id; can be exposed as string in API (e.g. `id`) |
| `filename`     | string   | Original filename from upload (optional, for audit) |
| `content_type` | string   | MIME type (e.g. `application/pdf`, `text/plain`) |
| `size_bytes`   | int      | Size of uploaded file in bytes |
| `extracted_text`| string  | Extracted plain text (UTF-8) |
| `status`      | string   | e.g. `success`, `empty`, `failed` (for optional future use) |
| `created_at`   | datetime | UTC timestamp of creation |

**Validation / rules** (from spec):

- `size_bytes` must not exceed the configured max document size.
- `content_type` must be one of the supported types (e.g. `text/plain`, `application/pdf`); reject others before persisting.
- `extracted_text` may be empty string when no text could be extracted (e.g. image-only PDF).

**Lifecycle**: Created when a document is successfully processed (and optionally on failure with `status: failed` and empty or error message). No state transitions; records are append-only.

## Storage

- **Database**: One MongoDB database (name from config).
- **Collection**: One collection for extraction records (e.g. `extractions`).
- **Indexes**: `created_at` (for ordering/cleanup); optionally `_id` for get-by-id if we add a GET endpoint later.

## Out of scope (v1)

- Storing raw file bytes.
- User/tenant separation; single-tenant.
- Soft delete or updates; records are immutable once written.
