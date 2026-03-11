# Research: Doc-to-Text API

**Feature**: 001-doc-to-text-api  
**Date**: 2026-03-10

## Technology Choices

### Stack (user-defined)

- **Docker**: Application and MongoDB run in containers; `docker-compose` for local dev.
- **Python**: Runtime; version 3.12 for current support and type hints.
- **FastAPI**: Minimal, async-capable web framework; fits “minimal libraries” and clear API surface.
- **MongoDB**: Store extraction results and metadata (e.g. filename, format, size, extracted text, created_at).

### Minimal libraries

- **Decision**: Use the smallest set of libraries that satisfy the spec: FastAPI, one driver for MongoDB (e.g. motor or pymongo), one PDF extraction library if PDF is supported in v1.
- **Rationale**: Constitution requires minimal dependencies and YAGNI; avoid extra frameworks (queues, caches, etc.) until needed.
- **Alternatives considered**: Celery/Redis for async jobs (rejected: not needed for “one request → one response”); multiple PDF libs (rejected: pick one for v1).

### Document formats (v1)

- **Decision**: Support at least **plain text** (e.g. `.txt`) and **PDF** in v1. Plain text is trivial (decode bytes); PDF requires one library (e.g. PyMuPDF or pdfplumber).
- **Rationale**: Spec asks for “at least one common format”; PDF + text covers most “document to text” use cases with minimal code.
- **Alternatives considered**: PDF only (narrow); many formats (violates minimal libs). Chosen: text + PDF.

### Persistence in MongoDB

- **Decision**: Persist each extraction as a **record** (e.g. document id, original filename, content type, size, extracted text, status, created_at). Optional: store raw bytes or not (v1: store only metadata + extracted text to keep storage small).
- **Rationale**: User requirement “armazene os dados em um banco de dados mongodb”; enables auditing, optional “get by id” later, and keeps API stateless (submit → process → save → return).
- **Alternatives considered**: No persistence (rejected: user asked for MongoDB); store file bytes (optional later; v1 can skip to reduce size).

### API shape

- **Decision**: Single primary endpoint: e.g. `POST /extract` (or `POST /documents/extract`) with multipart file upload; response: JSON with `text` (and optional `id`, `format`) or plain text. Errors return 4xx/5xx with clear messages.
- **Rationale**: Spec: one endpoint, one document per request; minimal surface; FastAPI supports multipart and JSON out of the box.
- **Alternatives considered**: Multiple endpoints for “upload” vs “extract” (rejected: more complexity); GraphQL (rejected: not required, adds libs).

## Resolved Items

- All technical context items from the plan are defined (no NEEDS CLARIFICATION).
- Constitution gates (single responsibility, YAGNI, testability, boundaries, minimal deps) are respected by the chosen structure and stack.
