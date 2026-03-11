# Tasks: Doc-to-Text API

**Input**: Design documents from `specs/001-doc-to-text-api/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec; optional test tasks included in Polish phase for critical paths.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md: `src/`, `src/api/`, `src/domain/`, `src/infra/`, `tests/`
- [x] T002 Initialize Python project with FastAPI and minimal deps: add `pyproject.toml` or `requirements.txt` (FastAPI, uvicorn, motor or pymongo, one PDF lib e.g. PyMuPDF or pdfplumber)
- [x] T003 [P] Configure linting and formatting (e.g. Ruff) in `pyproject.toml` or `ruff.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work until this phase is complete

- [x] T004 Add `src/infra/config.py`: settings from env (MONGODB_URI, MONGODB_DB, MAX_DOCUMENT_SIZE_BYTES), with sensible defaults
- [x] T005 [P] Add `Dockerfile` for Python 3.12 app (copy src, install deps, run uvicorn)
- [x] T006 [P] Add `docker-compose.yml` with app service and MongoDB; expose app on 8000, MongoDB on 27017
- [x] T007 Implement `src/infra/storage.py`: MongoDB repository for ExtractionRecord (collection `extractions`); save(document) returning id; optional get_by_id; use config for connection
- [x] T008 Add `src/main.py`: FastAPI app, lifespan for MongoDB connect/disconnect, include router from `src/api/routes.py`

**Checkpoint**: Foundation ready; user story implementation can begin

---

## Phase 3: User Story 1 – Enviar documento e receber texto (Priority: P1) 🎯 MVP

**Goal**: Consumer sends a document and receives extracted plain text in response.

**Independent Test**: POST a supported document to `/extract` and assert response contains `text` (and optional `id`); empty or image-only document returns empty text or clear indication.

### Implementation for User Story 1

- [x] T009 [P] [US1] Define ExtractionRecord schema (fields per data-model.md) in `src/infra/storage.py` or `src/infra/schemas.py`
- [x] T010 [US1] Implement `src/domain/extractor.py`: extraction interface (e.g. `extract(bytes, content_type) -> str`) and implementation(s) for `text/plain` and `application/pdf`; return UTF-8 text; empty content returns empty string
- [x] T011 [US1] Implement POST `/extract` in `src/api/routes.py`: multipart file upload (field `file`), call extractor, persist via storage, return JSON `{ "text", "id", "format" }` per contracts/api.md
- [x] T012 [US1] Ensure response encoding UTF-8 and handle empty extracted text (return empty string or explicit indicator) per spec edge cases

**Checkpoint**: User Story 1 is functional and independently testable

---

## Phase 4: User Story 2 – Rejeitar formatos não suportados (Priority: P2)

**Goal**: Reject unsupported formats and missing document with explicit 400 error messages.

**Independent Test**: POST without file or with unsupported content-type; assert 400 and `detail` indicates "document required" or "unsupported format".

### Implementation for User Story 2

- [x] T013 [US2] In `src/api/routes.py` validate file is present and content-type is in allowed list (e.g. `text/plain`, `application/pdf`); return 400 with clear `detail` for missing file or unsupported format
- [x] T014 [US2] Document supported formats in OpenAPI description or error message (per FR-002 and contracts/api.md)

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 – Limites de tamanho e resposta a falhas (Priority: P3)

**Goal**: Reject oversized documents with 413; return generic 500 on extraction failure without exposing internals.

**Independent Test**: POST document over max size → 413 with message; POST corrupted or failing document → 500 with generic message only.

### Implementation for User Story 3

- [x] T015 [US3] In `src/api/routes.py` enforce max document size (from config); reject with 413 and JSON `detail` stating the limit per contracts/api.md
- [x] T016 [US3] Wrap extraction and storage in try/except in `src/api/routes.py`; on failure return 500 with generic `detail` only (no stack trace or internal details) per FR-006

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements across stories and validation

- [x] T017 [P] Add `tests/conftest.py` with FastAPI test client fixture and optional test MongoDB or in-memory fixture
- [x] T018 [P] Add `tests/test_api.py`: at least one happy-path POST `/extract` and one 400/413/500 case
- [x] T019 [P] Add `tests/test_domain.py`: unit tests for extractor (plain text and PDF) in `src/domain/extractor.py`
- [ ] T020 Run quickstart.md validation: `docker compose up`, then `curl -X POST http://localhost:8000/extract -F "file=@<sample>.pdf"` and verify response

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Foundational; US2/US3 build on US1 endpoint
- **Polish (Phase 6)**: Depends on completion of desired user stories

### User Story Dependencies

- **US1 (P1)**: After Phase 2 only; no dependency on US2/US3
- **US2 (P2)**: After Phase 2; extends same endpoint as US1 (validation)
- **US3 (P3)**: After Phase 2; extends same endpoint (size + error handling)

### Within Each User Story

- US1: Schema/storage → extractor → route → encoding/empty handling
- US2: Validation in route + docs
- US3: Size check and exception handling in route

### Parallel Opportunities

- Phase 1: T003 [P] with T001/T002
- Phase 2: T005, T006 [P] in parallel; T004 before T007
- Phase 3: T009 [P] can run with T010 prep
- Phase 6: T017, T018, T019 [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational  
3. Complete Phase 3: User Story 1  
4. **STOP and VALIDATE**: Test POST /extract with a document  
5. Deploy/demo if ready  

### Incremental Delivery

1. Setup + Foundational → foundation ready  
2. Add US1 → test independently → MVP  
3. Add US2 → test validation → deploy  
4. Add US3 → test limits and errors → deploy  
5. Polish (tests, quickstart validation)  

---

## Notes

- [P] = parallelizable where noted
- [USn] maps to spec user stories for traceability
- Each story is independently testable via POST /extract
- Commit after each task or logical group
- Paths follow plan.md: `src/main.py`, `src/api/routes.py`, `src/domain/extractor.py`, `src/infra/storage.py`, `src/infra/config.py`
