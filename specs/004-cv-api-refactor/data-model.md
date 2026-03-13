# Data Model: CV Extraction API Refactor

This document describes the key entities and their attributes for the refactored extraction API. Storage schema and API payload shapes remain unchanged; only structure and validation are clarified.

---

## Entities

### Extraction record (storage)

Persisted document representing one extraction. Schema unchanged.

| Field           | Type     | Description                          |
|----------------|----------|--------------------------------------|
| filename       | str \| None | Original upload filename             |
| content_type   | str      | MIME type (e.g. application/pdf)     |
| size_bytes     | int      | Size of uploaded file in bytes        |
| extracted_text | str      | Extracted text content               |
| status         | str      | e.g. "success"                       |
| created_at     | datetime | Creation timestamp (UTC)             |

**Validation**: All fields present; content_type and status are non-empty. No schema migration.

---

### Upload request (in-memory / API)

Represents the client’s upload: file stream plus metadata. Validated before processing.

| Concept        | Source        | Description                          |
|----------------|---------------|--------------------------------------|
| file           | UploadFile    | Stream; presence and type validated  |
| content_type   | UploadFile    | Declared MIME type                   |
| filename       | UploadFile    | Optional filename                    |
| size           | Stream / header | Checked against max_document_size  |

Validation rules: file required; content_type in allowed list (constants); size ≤ max_document_size_bytes.

---

### Validation result (in-memory)

Output of the validation layer; consumed by the route or extraction service.

| Variant | Fields / meaning                                      |
|---------|--------------------------------------------------------|
| Ok      | Validated file metadata (and stream or buffer for processing). |
| Error   | Error kind (e.g. missing_file, unsupported_type, size_exceeded), message, optional HTTP status. |

No persistence; used only to decide whether to proceed or return an error response.

---

### Extraction strategy (domain contract)

Contract for “extract text from bytes for a given type.” Not a data entity; one strategy instance per supported content type.

| Concept    | Description                                                |
|-----------|------------------------------------------------------------|
| Input     | content: bytes; content_type used by registry to select strategy. |
| Output    | Extracted text (str) or raise; errors logged by caller or strategy. |

Implementations: PDF strategy (pdfplumber), plain-text strategy (decode). Registry maps content_type (constant) → strategy.

---

### API response (success)

Returned on successful extraction; shape unchanged.

| Field   | Type | Description        |
|---------|------|--------------------|
| text    | str  | Extracted text     |
| id      | str  | Stored record id   |
| format  | str  | Content type string|

Validated by a Pydantic response model so the schema stays consistent.

---

### API response (error)

Validation and server errors keep current status codes (400, 413, 500) and a consistent error body shape (e.g. `detail`). Optional: single Pydantic model for error payloads.

---

## Constants (no schema change)

- **Collection name**: Single logical collection for extraction records; name defined as a constant (e.g. in `infra/constants.py`).
- **MIME types**: Supported content types (e.g. PDF, plain text) defined as constants in `domain/constants.py` and used in config and validation.
