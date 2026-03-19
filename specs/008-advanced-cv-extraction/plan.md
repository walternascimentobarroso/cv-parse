# Implementation Plan: Advanced Structured CV Extraction

**Branch**: `008-advanced-cv-extraction` | **Date**: 2026-03-18 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification + architecture notes (modular extractors, DDD layers, fixtures, incremental delivery).

## Summary

Extend CV parsing so multiple experiences, STAR-style narratives, categorized skills, languages, and richer personal fields are extracted **deterministically**, with **additive** `parsed_data` only. Implementation uses **domain protocols** + **infra extractors** + a thin **application** orchestrator, incremental steps, golden fixtures (`profile.pdf` / `profile_expected.json`), optional **feature flag** for rollback, and structured **logging**.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Motor, pdfplumber, pydantic-settings (unchanged)  
**Storage**: MongoDB — same collection; `parsed_data` grows additively  
**Testing**: pytest; golden JSON + unit tests on section text  
**Target Platform**: Linux/macOS server (existing API)  
**Project Type**: Web service (backend)  
**Performance Goals**: No significant p95 regression vs current parse path (spec SC-003 spirit for personal info feature)  
**Constraints**: No LLM; domain must not import FastAPI/Motor; text-in / dict-out testability  
**Scale/Scope**: Single-threaded parse per upload; typical CV &lt; 20 pages

## Constitution Check

*GATE: Passed.*

| Principle | Status |
|-----------|--------|
| I. Single-Responsibility | Extractors per section; small functions |
| II. YAGNI / no LLM | Regex/heuristics only; optional flag minimal |
| III. Testable / isolated | Extractors unit-tested without PDF |
| IV. Explicit boundaries | Domain protocols; infra implementations |
| V. Consistent style | Existing logging/ruff patterns |

**Post–Phase 1**: Design keeps boundaries clear; no new framework deps.

## Project Structure

### Documentation (this feature)

```text
specs/008-advanced-cv-extraction/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── parsed-data.md
│   └── extractor-protocols.md
└── tasks.md              # /speckit.tasks (not created here)
```

### Source code (target layout)

```text
src/
├── application/
│   └── cv_parsing.py           # Orchestrate section extractors → CvParsedData
├── domain/
│   ├── cv_parser.py            # Facade or thin delegate to application
│   ├── section_detector.py     # Existing; may extend headers
│   ├── personal_info/          # Existing; extend for location/website/name
│   └── cv_extraction/          # NEW: protocols (Typing.Protocol)
│       └── protocols.py
├── infra/
│   └── cv_extractors/          # NEW: Experience, Skills, Languages, Certifications
│       ├── registry.py
│       ├── experience.py
│       ├── skills_categorized.py
│       ├── languages.py
│       └── certification_structured.py
tests/
├── fixtures/
│   ├── profile.pdf             # Anonymized real CV (or integration-only)
│   └── profile_expected.json
├── domain/
└── application/
```

**Structure Decision**: Add `application/cv_parsing.py` and `infra/cv_extractors/` without moving PDF MIME `ExtractorRegistry` (that stays document-level).

## Phases

### Phase 0 — Research

Completed in [research.md](./research.md): orchestration placement, additive keys, feature flag, STAR order, fixtures, logging, separate CV registry.

### Phase 1 — Design

- [data-model.md](./data-model.md) — entities and additive fields  
- [contracts/parsed-data.md](./contracts/parsed-data.md) — consumer contract  
- [contracts/extractor-protocols.md](./contracts/extractor-protocols.md) — internal extractor contract  
- [quickstart.md](./quickstart.md) — dev workflow  

### Phase 2 — Tasks

Deferred to **`/speckit.tasks`**.

## Incremental delivery (implementation order)

1. **Personal info**: Add `name`, `location`, `website` in domain personal_info path (additive).  
2. **Experience**: New infra `ExperienceExtractor` — multi-block detection + STAR merge; wire via application; optional flag fallback to legacy parser.  
3. **Skills**: `SkillsExtractor` — hard/soft sections + maintain flat `skills`.  
4. **Languages**: `LanguagesExtractor` + `parsed_data.languages`.  
5. **Certifications**: `certification_details` alongside string list.  
6. **Integration**: Golden test + logs + DEBUG hooks.

## Risk mitigation

- Keep legacy `parse_experience_section` callable when flag off.  
- Regression: existing pytest suites must pass unchanged assertions on legacy keys.  
- Fixture drift: golden test asserts counts + key fields, not full string equality where fragile.

## Observability

- INFO: stage timing (`personal_info`, `experience`, `skills`, `languages`, `merge`).  
- DEBUG: block counts, section names (no full email/body at INFO).

## Complexity Tracking

No constitution violations requiring justification.
