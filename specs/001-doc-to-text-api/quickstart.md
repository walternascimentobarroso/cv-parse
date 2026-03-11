# Quickstart: Doc-to-Text API

**Feature**: 001-doc-to-text-api  
**Date**: 2026-03-10

## Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.12+ and `pip` for local run without Docker

## Run with Docker

1. From repository root:

   ```bash
   docker compose up -d
   ```

   This starts the API service and MongoDB (see `docker-compose.yml`). Default: API on port 8000, MongoDB on 27017.

2. Check health (if implemented):

   ```bash
   curl http://localhost:8000/health
   ```

3. Extract text from a document:

   ```bash
   curl -X POST http://localhost:8000/extract -F "file=@/path/to/document.pdf"
   ```

   Or for a text file:

   ```bash
   curl -X POST http://localhost:8000/extract -F "file=@/path/to/document.txt"
   ```

4. Expected: JSON response with `text` (and optionally `id`, `format`). For unsupported format or missing file, expect 4xx with `detail` message.

## Environment variables (typical)

| Variable           | Description                    | Example        |
|--------------------|--------------------------------|----------------|
| `MONGODB_URI`      | MongoDB connection string      | `mongodb://mongodb:27017` |
| `MONGODB_DB`       | Database name                  | `doctotext`    |
| `MAX_DOCUMENT_SIZE_BYTES` | Max upload size (bytes) | `10485760` (10 MB) |

Adjust in `docker-compose.yml` or `.env` as needed.

## Project layout (reference)

- `src/`: Application code (FastAPI app, api routes, domain extractor, infra storage/config).
- `tests/`: Tests (API and domain).
- `docker-compose.yml`: App + MongoDB.
- `Dockerfile`: Python app image.

## Contract

See [contracts/api.md](./contracts/api.md) for request/response shapes and error codes.
