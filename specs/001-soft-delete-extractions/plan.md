# Implementation Plan: Soft Delete and Restore for Extractions

**Branch**: `001-soft-delete-extractions` | **Date**: 2026-03-16 | **Spec**: `specs/001-soft-delete-extractions/spec.md`  
**Input**: Feature specification for soft delete and restore behavior in the Extractions API.

**Note**: This plan covers data model, repository, query behavior, API endpoints, timestamps, error handling, and logging for soft delete, restore, and force delete of extractions.

## Summary

Implement soft delete semantics for extractions by extending the existing MongoDB-backed Extractions API so that:

- Extractions gain `updated_at` and nullable `deleted_at` timestamps in the schema.
- All default read paths ignore records where `deleted_at` is set.
- The repository exposes `soft_delete`, `restore`, and `force_delete` operations that encapsulate the data access and timestamp updates.
- The API defines `DELETE /extractions/{id}`, `POST /extractions/{id}/restore`, and `DELETE /extractions/{id}/force` endpoints that delegate to the repository and enforce domain rules and error handling.
- Logging is added for soft delete, restore, and force delete operations without leaking internal implementation details.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Motor (async MongoDB driver), Pydantic (v2), pdfplumber, pydantic-settings  
**Storage**: MongoDB, accessed via Motor, with existing collections for extractions  
**Testing**: pytest, httpx for API tests, existing test layout under `tests/`  
**Target Platform**: Linux server (container-friendly), HTTP API  
**Project Type**: Web-service (HTTP API) with DDD-inspired layering (domain, infra, api)  
**Performance Goals**: Maintain existing latency characteristics; soft delete must not materially degrade typical list/get performance for expected dataset sizes  
**Constraints**: Respect DDD boundaries (no business logic in routes; infra owns DB access; domain owns rules). Use async IO for MongoDB operations. Keep changes incremental and backwards compatible for existing consumers except for the new soft delete semantics on delete.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility Modules**:  
  - Repository remains responsible only for data access and persistence concerns (including timestamp updates and filters).  
  - API routes remain thin controllers delegating to domain/services or repository abstractions, with no embedded business logic beyond wiring and error mapping.
- **Simplicity Over Features (YAGNI)**:  
  - No additional lifecycle states beyond active vs soft-deleted.  
  - No background cleanup jobs, archival logic, or multi-tenant deletion policies added.  
  - Reuse existing DDD structure and dependency patterns.
- **Testable, Isolated Code**:  
  - Repository methods (`soft_delete`, `restore`, `force_delete`) accept explicit identifiers and return clear results/errors, making them testable with Motor or fakes.  
  - Domain-level behavior (e.g., “restore only when soft deleted”) is enforced in a single place that can be exercised by unit tests.  
  - API tests validate wiring and HTTP surface with httpx.
- **Explicit Boundaries & Dependencies**:  
  - Domain layer does not take direct dependencies on Motor or FastAPI constructs.  
  - Infra layer continues to encapsulate Motor usage; API layer depends on domain/infra abstractions only.  
  - No new global singletons; dependencies are injected via existing mechanisms.
- **Consistent Style & Readability**:  
  - Follow existing file and naming conventions (`src/api/routes.py`, `src/infra/schemas.py`, `src/infra/storage.py` or equivalent repository module).  
  - Use clear, intention-revealing names for new fields and methods.

All gates can be satisfied with the planned changes. No constitution violations are expected; **Complexity Tracking** can remain empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-soft-delete-extractions/
├── spec.md
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (this plan will keep research minimal; no open NEEDS CLARIFICATION)
├── data-model.md        # Phase 1 output describing Extraction state and timestamps
├── quickstart.md        # Phase 1 output for how to work with soft delete
├── contracts/           # Phase 1 output for API surface of Extractions
└── tasks.md             # Phase 2 output (/speckit.tasks, not created here)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes.py            # Extractions HTTP endpoints (add soft delete/restore/force routes)
├── domain/
│   ├── extractor.py         # Domain logic for extractions (ensure behavior consistent with soft delete)
│   └── document_extractor_contracts.py
├── infra/
│   ├── schemas.py           # Pydantic models for extractions (add updated_at, deleted_at)
│   ├── storage.py           # MongoDB access layer / repository for extractions (add soft_delete, restore, force_delete)
│   ├── config.py
│   └── logging_config.py

tests/
├── api/
│   └── test_extractions_soft_delete.py   # New tests for endpoints and behavior
├── domain/
│   └── ...                               # Existing domain tests; extend if needed
└── infra/
    └── test_extraction_repository.py     # New/updated tests for repository methods
```

**Structure Decision**: Use the existing `src/api`, `src/domain`, and `src/infra` folders. Implement soft delete entirely within this structure: schema and repository in `infra`, any domain rules in `domain`, and HTTP surface in `api`.

## Complexity Tracking

No constitution violations identified; this section remains empty unless future design changes introduce justified complexity.

