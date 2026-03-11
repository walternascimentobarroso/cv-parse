# Implementation Plan: Doc-to-Text API

**Branch**: `001-doc-to-text-api` | **Date**: 2026-03-10 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-doc-to-text-api/spec.md`

## Summary

Simple API that accepts document uploads, extracts plain text, and returns it to the caller. Data (extraction results and metadata) is stored in MongoDB. Stack: Docker, Python, FastAPI, MongoDB; minimal dependencies. Aligns with constitution: single-responsibility modules, YAGNI, testable code, explicit boundaries, minimal libraries.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, minimal libs (e.g. PyMuPDF or pdfplumber for PDF; one extractor per format)  
**Storage**: MongoDB (persist extraction records: document metadata + extracted text)  
**Testing**: pytest, httpx for API tests; optional in-memory/fake MongoDB for isolation  
**Target Platform**: Linux in Docker; local/dev and single-instance deployment  
**Project Type**: web-service (REST API)  
**Performance Goals**: Response within seconds for typical document sizes; no high-throughput target  
**Constraints**: Minimal libraries; run with Docker; single service + MongoDB  
**Scale/Scope**: Small: low concurrency, single instance; documents and records stored in one MongoDB database

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility**: API layer, extraction logic, and persistence are separated (domain/infra boundaries).
- **YAGNI / Simplicity**: No extra layers; only one document format required initially (e.g. PDF or plain text); minimal dependencies.
- **Testable, Isolated**: Extraction and persistence behind interfaces/adapters; tests can use fakes or in-memory DB.
- **Explicit Boundaries**: Domain (extract text from bytes) vs infrastructure (HTTP, MongoDB) clearly separated; dependencies injectable.
- **Readability**: Consistent style, descriptive names; lint/formatter (e.g. Ruff) configured.
- **Clean Code constraints**: Limited scope (one endpoint for submit + get text); few layers (api, domain, infra); minimal dependencies; no premature optimization.

*Post–Phase 1*: Design uses domain + infra + API; storage in MongoDB is the only persistence; contracts and data model documented. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-doc-to-text-api/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (API contract)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── main.py              # FastAPI app entry
├── api/
│   └── routes.py        # POST /extract (or /documents/extract) endpoint
├── domain/
│   └── extractor.py     # Text extraction (interface + impl for supported formats)
└── infra/
    ├── storage.py       # MongoDB persistence (repository/adapter)
    └── config.py        # Settings (env, limits)

tests/
├── conftest.py          # Fixtures (test client, fake or test DB)
├── test_api.py          # API contract / integration tests
└── test_domain.py       # Extraction logic tests (unit)

docker-compose.yml       # app + MongoDB
Dockerfile               # Python app image
```

**Structure Decision**: Single backend service. `api/` handles HTTP; `domain/` holds extraction logic (format-agnostic interface); `infra/` holds MongoDB and config. No frontend; no extra services.

## Complexity Tracking

No constitution violations requiring justification. MongoDB is the only persistence; one extractor per format keeps domain simple.
