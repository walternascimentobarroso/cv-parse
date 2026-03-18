# Implementation Plan: Extract Personal Information from CV

**Branch**: `007-extract-personal-info` | **Date**: 2026-03-18 | **Spec**: `specs/007-extract-personal-info/spec.md`
**Input**: Feature specification from `specs/007-extract-personal-info/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extract, normalize, and validate personal information from CVs into a new
`parsed_data.personal_info` section (full_name, email, phone, linkedin, github,
summary) using deterministic rules for email and links, heuristic parsing for
name and summary, and integrating into the existing extractor pipeline without
breaking the current `parsed_data` structure.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Motor (MongoDB), pdfplumber, Pydantic, project-specific parsing utilities  
**Storage**: MongoDB (existing flexible schema; no new collections)  
**Testing**: pytest, httpx (for API tests)  
**Target Platform**: Linux container (Docker), local development on macOS  
**Project Type**: web-service (FastAPI API with domain/infrastructure separation)  
**Performance Goals**: Preserve existing latency budgets; personal-info parsing adds ≤50 ms p95 per request in test envs  
**Constraints**: No AI/LLM or external NLP dependencies; must remain backward compatible with existing `parsed_data` shape  
**Scale/Scope**: Single API service; scope limited to CV personal information extraction and normalization

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility Modules**: Personal information extraction will be
  encapsulated in a dedicated `PersonalInfo` entity and `PersonalInfoExtractor`
  domain service.  
  **Status**: Pass.
- **Simplicity Over Features (YAGNI)**: The feature uses deterministic regex and
  heuristic rules only; no new AI/LLM dependencies or speculative abstractions
  beyond what is needed for future pluggable strategies.  
  **Status**: Pass.
- **Testable, Isolated Code**: Parsing and normalization will be implemented as
  pure or side-effect-free functions in the domain layer, with unit tests for
  edge cases.  
  **Status**: Pass.
- **Explicit Boundaries & Dependencies**: Domain objects and services will not
  depend on FastAPI, Motor, or pdfplumber; infrastructure code will adapt raw
  text into domain calls.  
  **Status**: Pass.
- **Consistent Style & Readability**: New modules will follow existing project
  style (type hints, small functions, early returns) and keep naming aligned
  with current domain/infrastructure organization.  
  **Status**: Pass.
- **CV Parsing System Principles**:
  - Store personal data under `parsed_data.personal_info` with the required
    keys.
  - Use deterministic extraction for email and links; heuristic, non-LLM rules
    for name and summary.
  - Normalize and validate all fields at the domain boundary.
  - Keep parsing in the domain layer; infra handles PDF/text only.  
  **Status**: Pass.

## Project Structure

### Documentation (this feature)

```text
specs/007-extract-personal-info/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── domain/
│   ├── personal_info/
│   │   ├── entities/
│   │   │   └── personal_info.py
│   │   └── services/
│   │       └── personal_info_extractor.py
│   └── cv/
│       └── parsing/  # existing CV parsing/domain modules (no breaking changes)
├── infra/
│   ├── parsing/
│   │   └── text_extractor.py  # existing raw_text extraction from documents
│   └── api/
│       └── fastapi/
│           └── routes/        # existing FastAPI routes invoking the pipeline
└── api/
    └── pipeline/
        └── extractor.py       # orchestrates extraction steps, extended to call PersonalInfoExtractor

tests/
├── domain/
│   └── personal_info/
│       └── test_personal_info_extractor.py
├── api/
│   └── test_extractor_personal_info_integration.py
└── infra/
    └── parsing/
        └── test_text_extractor_existing.py  # if needed for regression coverage
```

**Structure Decision**: Single backend project with explicit `domain/`,
`infra/`, and `api/` layers. Personal information parsing lives under
`domain/personal_info/` with a dedicated entity and extractor service. The
existing extractor pipeline is extended (not replaced) to invoke the new domain
service and attach `personal_info` to `parsed_data` while preserving the rest of
the structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
