# Implementation Plan: Structured CV Parsing (without LLM)

**Branch**: `006-structured-cv-parsing` | **Date**: 2026-03-16 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/006-structured-cv-parsing/spec.md`

## Summary

Implement a deterministic CV parser in the `domain/` layer that takes extracted PDF text and produces structured sections (experience, education, skills, certifications), leaving API routes thin and persisting both raw and structured data in MongoDB. The parser is composed of small, testable components (section detector, section-specific parsers, and an orchestrator) and relies only on section detection, regex/pattern matching, and keyword dictionaries—no LLMs or external AI services.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Motor (async MongoDB driver), Pydantic, pdfplumber, pydantic-settings  
**Storage**: MongoDB (existing CV collection; extended document shape with `parsed_data`)  
**Testing**: pytest, httpx (for API tests)  
**Target Platform**: Linux server (containerised deployment)  
**Project Type**: Web service (HTTP API)  
**Performance Goals**: Parsing should complete within a single request cycle for typical CV sizes (≤ 2–3 seconds p95 for upload+parse+store).  
**Constraints**: Deterministic, no outbound calls to AI/LLM providers; keep parsing logic CPU-only and memory-light to run alongside existing API workloads.  
**Scale/Scope**: Single service, modest traffic; feature scope limited to CV upload and parsing, with no additional user-facing UI.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility Modules**:  
  - Section detector, experience parser, education parser, skills extractor, and CV parser orchestrator are each responsible for a single concern in the parsing pipeline.  
  - API routes only orchestrate HTTP concerns (validation, wiring to domain) and do not contain parsing logic.

- **Simplicity Over Features (YAGNI)**:  
  - Only deterministic parsing is implemented; no generic NLP layer, no plugin system, and no speculative features (e.g., multi-language support) beyond the current spec.  
  - Parsing rules start simple (headings list, date/company heuristics, skills dictionary) and will evolve only when concrete CV samples require it.

- **Testable, Isolated Code**:  
  - Parsing functions in `domain/` take plain text/sections as input and return structured data without performing IO, making them trivial to unit test.  
  - MongoDB access stays in `infra/` adapters already covered by existing patterns; tests can inject raw text and assert on parsed_data without hitting the database.

- **Explicit Boundaries & Dependencies**:  
  - `api/` → `domain/` → `infra/` dependency flow is preserved: routes call domain parsing services, which return pure data structures that `infra` persists.  
  - Domain parsers depend only on standard library and shared configuration (e.g., skills list), not on FastAPI, Motor, or other infrastructure details.

- **Consistent Style & Readability**:  
  - New modules follow existing Python style (type hints, small functions, descriptive names) and repository layout (`src/api`, `src/domain`, `src/infra`).  
  - No commented-out code or dead code is introduced; comments are reserved for non-obvious heuristics in parsing.

All gates are satisfied with the planned design; no constitution violations are expected for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/006-structured-cv-parsing/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes.py                # CV upload endpoint wires into domain CV parser
├── domain/
│   ├── cv_parser.py             # Orchestrator: sections → structured parsed_data
│   ├── section_detector.py      # Raw text → sectioned text blocks
│   ├── experience_parser.py     # Experience section → list[ExperienceEntry]
│   ├── education_parser.py      # Education section → list[EducationEntry]
│   └── skills_extractor.py      # Skills section and/or full text → list[str]
└── infra/
    └── mongo_cv_repository.py   # MongoDB persistence for CV documents (existing, extended for parsed_data)

tests/
├── api/
│   └── test_cv_upload_parsing.py      # End-to-end tests for upload → parse → store
├── domain/
│   ├── test_section_detector.py       # Unit tests for heading detection and splitting
│   ├── test_experience_parser.py      # Unit tests for experience extraction heuristics
│   ├── test_education_parser.py       # Unit tests for education parsing
│   └── test_skills_extractor.py       # Unit tests for skills matching against dictionary
└── infra/
    └── test_mongo_cv_repository.py    # Persistence tests (existing patterns)
```

**Structure Decision**:  
Use the existing layered layout (`src/api`, `src/domain`, `src/infra` with mirrored `tests/`) and add a small set of focused domain modules for CV parsing. API routes remain thin controllers that delegate to the `cv_parser` orchestrator. MongoDB integration is handled by infra code that simply stores the extended CV document, keeping parsing logic and persistence concerns separate and testable.

## Complexity Tracking

No constitution violations or extra layers beyond the existing architecture are introduced, so no complexity justifications are required for this feature.

