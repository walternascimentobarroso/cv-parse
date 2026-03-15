# Extractions API Contract (005-extractions-crud-audit)

**Feature**: CRUD and Audit Timestamps  
**Date**: 2026-03-15

This document describes the HTTP API for extraction records. All endpoints return JSON unless noted. Timestamps are ISO 8601 (UTC).

## Base path

All extraction CRUD endpoints are under `/extractions`. The existing upload endpoint remains at `/extract`.

---

## Create extraction (upload)

**POST /extract** *(unchanged)*

- **Request**: `multipart/form-data` with file upload.
- **Response**: 200 — `{ "text": string, "id": string, "format": string }`.
- **Behavior**: Upload document, extract text, persist record with `created_at` set; `updated_at` and `deleted_at` null. Returns extraction id for use in GET/PATCH/DELETE.

---

## List extractions

**GET /extractions**

- **Response**: 200 — Array of extraction detail objects (see Extraction detail shape below).
- **Behavior**: Returns only non–soft-deleted records (`deleted_at` null). No pagination in this feature.

---

## Get extraction by id

**GET /extractions/{id}**

- **Path**: `id` — 24-character hex string (MongoDB ObjectId).
- **Response**: 200 — Extraction detail object. 404 — Not found (invalid id or soft-deleted).

---

## Update extraction

**PATCH /extractions/{id}**

- **Path**: `id` — 24-character hex string.
- **Request body**: JSON object with allowed fields only (e.g. `extracted_text`). No `id`, `created_at`, `updated_at`, `deleted_at`.
- **Response**: 200 — Full extraction detail (same shape as GET by id). 404 — Not found. 422 — Validation error (invalid or disallowed fields).

---

## Soft delete extraction

**DELETE /extractions/{id}**

- **Path**: `id` — 24-character hex string.
- **Response**: 204 No Content on success. 404 — Not found (invalid id or already soft-deleted).
- **Behavior**: Sets `deleted_at` to current time; record is not physically removed. Record no longer appears in GET list or GET by id.

---

## Extraction detail shape (GET by id, list item, PATCH response)

- `id`: string (ObjectId as string)
- `filename`: string | null
- `content_type`: string
- `size_bytes`: integer
- `extracted_text`: string
- `status`: string
- `created_at`: string (ISO 8601)
- `updated_at`: string | null (ISO 8601; null until first update)

`deleted_at` is never returned in API responses.

---

## Error responses

- **400/404**: Invalid or missing id; record not found or soft-deleted.
- **422**: Request body validation failure (e.g. PATCH with invalid or disallowed fields).
- **500**: Server error (e.g. extraction or persistence failure).

Error body shape: `{ "detail": string }` or similar (project standard).
