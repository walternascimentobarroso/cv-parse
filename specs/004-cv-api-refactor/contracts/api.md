# API Contract: Doc-to-Text (CV Extraction)

This contract must remain **stable** across the refactor. No breaking changes to paths, methods, request/response shapes, or status codes.

---

## Base

- **Base path**: Application root (e.g. `/`).
- **Content negotiation**: Request: multipart form for file upload. Response: JSON.

---

## Endpoints

### GET /health

- **Purpose**: Liveness/readiness.
- **Request**: No body.
- **Response**: `200 OK`
- **Body**: `{ "status": "ok" }`
- **Contract**: Unchanged.

---

### POST /extract

- **Purpose**: Upload a document and receive extracted text plus a stored record id.
- **Request**:
  - Method: `POST`
  - Content-Type: `multipart/form-data`
  - Body: one file part (name and key as in current implementation, e.g. `file`).
- **Success**: `200 OK`
  - Body: JSON with:
    - `text` (string): extracted text
    - `id` (string): stored record id (e.g. MongoDB ObjectId as string)
    - `format` (string): content type of the uploaded file (e.g. `application/pdf`, `text/plain`)
- **Validation errors** (unchanged behavior):
  - Missing file or invalid request: `400 Bad Request` with a `detail` message (e.g. "Document file is required.", "Unsupported document format. Supported formats: ...").
  - File exceeds maximum size: `413 Request Entity Too Large` with a `detail` message (e.g. "Document exceeds maximum allowed size (N bytes).").
- **Server error**: Extraction or storage failure: `500 Internal Server Error` with a generic `detail` (e.g. "Failed to process document."). No stack trace or internal details in the response.
- **Supported types**: At least `application/pdf` and `text/plain` (configurable; values must be represented by constants after refactor).
- **Contract**: Same status codes and same response field names and types; only internal structure (constants, DI, validation layer, strategies, logging) may change.

---

## Out of scope for this refactor

- New endpoints or new query/body parameters.
- Changes to the storage document schema or collection name semantics.
- New extraction formats or options.
