# API Contract: Doc-to-Text API

**Feature**: 001-doc-to-text-api  
**Date**: 2026-03-10

## Base

- **Protocol**: HTTP/1.1 over HTTPS (or HTTP in dev).
- **Base path**: `/` (e.g. `POST /extract` or configurable prefix).
- **Request/response encoding**: UTF-8. Binary upload via multipart.

---

## Endpoint: Extract text from document

**Method**: `POST`  
**Path**: `/extract` (or `/documents/extract`)  
**Description**: Accepts a single document file, extracts plain text, persists a record in MongoDB, and returns the extracted text (and optional metadata).

### Request

- **Content-Type**: `multipart/form-data`
- **Body**: One file part (name e.g. `file` or `document`). No other parts required for v1.

**Example** (curl):

```bash
curl -X POST http://localhost:8000/extract -F "file=@document.pdf"
```

### Response: Success (200 OK)

- **Content-Type**: `application/json` (default) or `text/plain` if requested via `Accept` (optional).
- **JSON body** (when `application/json`):

| Field   | Type   | Description                    |
|--------|--------|--------------------------------|
| `text` | string | Extracted plain text (UTF-8).  |
| `id`   | string | (Optional) Stored record id.   |
| `format` | string | (Optional) Detected/used format. |

- **Alternative**: Return `text/plain` with only the extracted text (no JSON) when Accept is `text/plain`.

**Example** (JSON):

```json
{
  "text": "Hello world...",
  "id": "507f1f77bcf86cd799439011",
  "format": "application/pdf"
}
```

### Response: Client errors (4xx)

- **400 Bad Request**: Missing file, invalid form, or unsupported format. Body: JSON `{"detail": "..."}` (or array of errors). Message must indicate “document required” or “unsupported format” as per spec.
- **413 Payload Too Large**: Document exceeds max size. Body: JSON `{"detail": "..."}` with clear mention of limit.

### Response: Server errors (5xx)

- **500 Internal Server Error**: Processing failed (e.g. corrupted file, extraction error). Body: JSON `{"detail": "..."}` with a generic message only (no stack trace or internal details).

---

## Health / readiness (optional)

- **GET /health** or **GET /**: Returns 200 when the app and (optionally) MongoDB are reachable. No contract detail required for v1.

---

## Consistency

- All error responses use a consistent shape (e.g. FastAPI default: `{"detail": ...}`).
- Supported formats (e.g. `text/plain`, `application/pdf`) are documented in the API description or error message when an unsupported format is sent.
