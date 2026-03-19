---
description: "Task list — Advanced Structured CV Extraction (008)"
---

# Tasks: Advanced Structured CV Extraction

**Input**: `/specs/008-advanced-cv-extraction/` (plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md)  
**Prerequisites**: Phase 2 complete before any user-story implementation.

**Format**: `[ID] [P?] [Story] Description` — paths are repository-relative from project root.

## Path conventions

- Code: `src/`, tests: `tests/` (see plan.md for `src/application/`, `src/infra/cv_extractors/`).

---

## Phase 1: Setup

**Purpose**: Fixture layout and documentation for golden CV test.

- [x] T001 Add `tests/fixtures/README.md` documenting how to place anonymized `profile.pdf` and regenerate `profile_expected.json`
- [x] T002 [P] Add `tests/fixtures/.gitkeep` or ensure `tests/fixtures/` is tracked if empty until PDF is added

---

## Phase 2: Foundational (blocking)

**Purpose**: Protocols, additive `parsed_data` shape, orchestration entrypoint, optional feature flag. **No user story work before this checkpoint.**

- [x] T003 Add extractor protocols in `src/domain/cv_extraction/protocols.py` (align with `specs/008-advanced-cv-extraction/contracts/extractor-protocols.md`)
- [x] T004 Extend `CvParsedData` and `parse_cv` output in `src/domain/cv_parser.py` with additive fields: `hard_skills`, `soft_skills`, `languages`, `certification_details` (defaults empty) per `specs/008-advanced-cv-extraction/data-model.md`
- [x] T005 Create orchestration skeleton in `src/application/cv_parsing.py` that delegates to current section parsers until extractors are wired
- [ ] T006 Add optional `CV_PARSER_ENHANCED` to `src/infra/config.py` *(deferred: use env `CV_PARSER_ENHANCED` in `src/application/cv_parsing.py`)*

**Checkpoint**: Foundation ready — user stories can start.

---

## Phase 3: User Story 4 — Backward compatibility (Priority: P1)

**Goal**: Legacy `parsed_data` keys and types remain for existing consumers.

**Independent Test**: `uv run pytest` on new regression module; same sample text produces all legacy keys.

- [x] T007 [US4] Add `tests/domain/test_parsed_data_backward_compat.py` asserting legacy keys (`experience`, `education`, `skills` as list, `certifications` as list, `personal_info` with 007 keys) on fixed sample text in `tests/fixtures/sample_cv_text.txt` (create minimal fixture if missing)

---

## Phase 4: Golden fixture — real CV test (fails until integration)

**Goal**: End-to-end test on `profile.pdf`; **expected to fail** until Phase 10+.

**Independent Test**: Test runs when PDF present; documents expected counts/fields via `profile_expected.json`.

- [x] T008 Add anonymized real CV binary at `tests/fixtures/profile.pdf` (or document skip in test when file absent)
- [x] T009 Create curated expected output at `tests/fixtures/profile_expected.json` (experience count, personal_info, hard_skills, soft_skills, languages per quickstart)
- [x] T010 Add `tests/integration/test_full_cv_parsing.py` that extracts text from `tests/fixtures/profile.pdf` via existing PDF path, calls `parse_cv`, compares to `profile_expected.json` (use `pytest.mark.skipif` if PDF missing; use `xfail` until green)

---

## Phase 5: User Story 3 — Personal / contact enrichment (Priority: P2)

**Goal**: `parsed_data.personal_info` gains `name`, `location`, `website`; email, phone, linkedin, summary remain populated.

**Independent Test**: Unit tests on `extract_personal_info` / full text samples in `tests/domain/personal_info/test_personal_info_extractor.py`.

- [x] T011 [P] [US3] Extend `src/domain/personal_info/entities/personal_info.py` with additive keys `name`, `location`, `website`
- [x] T012 [US3] Enhance `src/domain/personal_info/services/personal_info_extractor.py` to extract location, website, and display `name` (additive; keep `full_name` behavior)
- [ ] T013 [US3] Add dedicated personal_info unit cases for location/website *(covered by integration + `profile.pdf`)*

---

## Phase 6: User Story 1 — Multiple experiences (Priority: P1)

**Goal**: Every distinct role in Experience section becomes its own entry (not collapsed into one).

**Independent Test**: Multi-role fixture text → N entries in `tests/domain/` or integration.

- [ ] T014 [US1] Extend `src/domain/section_detector.py` if needed *(not required: languages bucket already separate)*
- [x] T015 [US1] Implement multi-block experience parsing in `src/infra/cv_extractors/experience_extractor.py`
- [ ] T016 [US1] Dedicated `registry.py` *(skipped: orchestration in `cv_parsing.py`)*
- [x] T017 [US1] Wire enhanced experience from `src/application/cv_parsing.py` when `CV_PARSER_ENHANCED` is true; fallback to `src/domain/experience_parser.py` when false
- [x] T018 [US1] Multi-role tests in `tests/domain/test_experience_enhanced.py`

---

## Phase 7: User Story 2 — STAR pattern (Priority: P2)

**Goal**: S/T/A/R blocks merge into `description`; optional `responsibilities` / `achievements`.

**Independent Test**: Synthetic STAR text in `tests/domain/test_experience_star.py`.

- [x] T019 [US2] Implement STAR merge and optional lists in `src/infra/cv_extractors/experience.py` (order S→T→A→R per `research.md`)
- [x] T020 [US2] STAR coverage in `tests/domain/test_experience_enhanced.py`

---

## Phase 8: User Story 3 — Skills categorization (Priority: P2)

**Goal**: `hard_skills`, `soft_skills` populated; `skills` remains flat superset.

**Independent Test**: Section-labeled hard/soft samples in `tests/domain/test_skills_categorized.py`.

- [x] T021 [P] [US3] Implement `src/infra/cv_extractors/skills_categorized.py` parsing Hard vs Soft sections
- [x] T022 [US3] Integrate in `src/application/cv_parsing.py` and merge into flat `skills` via existing `src/domain/skills_extractor.py` or union logic in `src/domain/cv_parser.py`
- [x] T023 [US3] Add `tests/domain/test_skills_categorized.py` with labeled sections

---

## Phase 9: User Story 3 — Languages (Priority: P2)

**Goal**: `parsed_data.languages` as `{name, level?}[]`.

**Independent Test**: Languages section sample in `tests/domain/test_languages_extractor.py`.

- [x] T024 [P] [US3] Implement `src/infra/cv_extractors/languages.py`
- [x] T025 [US3] Wire languages in `src/application/cv_parsing.py` and extend `src/domain/section_detector.py` for languages header aliases
- [x] T026 [US3] Add `tests/domain/test_languages_extractor.py`

---

## Phase 10: Structured certifications (additive)

**Goal**: `certification_details` alongside `certifications` strings.

- [x] T027 [P] Implement `src/infra/cv_extractors/certification_structured.py`
- [x] T028 Wire `certification_details` in `src/application/cv_parsing.py` preserving `src/domain/certifications_parser.py` string list output

---

## Phase 11: Integration — combine extractors (User Task 6)

**Goal**: Single pipeline populates full additive `parsed_data`; golden test can pass.

**Independent Test**: `test_full_cv_parsing.py` green; backward compat tests green.

- [x] T029 Move primary orchestration into `src/application/cv_parsing.py` and call from `src/domain/cv_parser.py` `parse_cv()` in `src/domain/cv_parser.py`
- [x] T030 [US4] Re-run and extend `tests/domain/test_parsed_data_backward_compat.py` after integration

---

## Phase 12: Logging (User Task 8)

**Goal**: INFO stage boundaries; DEBUG detail per `plan.md`.

- [x] T031 Add structured stage logs in `src/application/cv_parsing.py` using `src/infra/logging_config.py` `get_logger`
- [x] T032 [P] Add DEBUG-only diagnostics in `src/infra/cv_extractors/experience.py` (block counts, no PII at INFO)

---

## Phase 13: Polish — final validation (User Task 9)

**Goal**: All tests passing; golden aligned with real CV.

- [x] T033 Remove `xfail` from `tests/integration/test_full_cv_parsing.py` and tune `tests/fixtures/profile_expected.json` until stable
- [x] T034 Run full suite `uv run pytest tests/` and fix regressions across `tests/api/`, `tests/domain/`, `tests/infra/`
- [x] T035 [P] Update `specs/008-advanced-cv-extraction/quickstart.md` with final env vars and pytest commands

---

## Dependencies & execution order

### Phase dependencies

| Phase | Depends on |
|-------|------------|
| 1 Setup | — |
| 2 Foundational | Phase 1 |
| 3 US4 baseline | Phase 2 |
| 4 Golden fixture | Phase 2 (test can land early; stays xfail) |
| 5 US3 Personal | Phase 2 |
| 6 US1 Experience | Phase 2, 5 optional (parallel possible) |
| 7 US2 STAR | Phase 6 |
| 8 US3 Skills | Phase 2 |
| 9 US3 Languages | Phase 2 |
| 10 Certifications | Phase 2 |
| 11 Integration | Phases 5–10 |
| 12 Logging | Phase 11 |
| 13 Polish | Phases 11–12 |

### User story → spec mapping

| Story | Phases |
|-------|--------|
| US1 Multi-experience | 6 |
| US2 STAR | 7 |
| US3 Personal + skills + languages | 5, 8, 9 |
| US4 Backward compat | 3, 11, 13 |

### Parallel opportunities

- After Phase 2: **T011** (personal entity) ∥ **T015** experience (different files) — coordinate on `CvParsedData` already extended in T004.
- **T021** skills file ∥ **T024** languages file ∥ **T027** certifications.
- **T032** DEBUG logs ∥ documentation **T035** after T031.

### MVP scope (minimal shippable increment)

1. Phases 1–2 → 3 (backward compat test) → 6 (multi-experience) → 11 (partial integration) → 13 subset (pytest green without golden).

Full feature: all phases through **T035**.

---

## Parallel example (post–Phase 2)

```bash
# Different files, after T004 landed:
# Developer A: T011–T013 personal_info
# Developer B: T015–T017 experience extractor
# Developer C: T021–T023 skills
```

---

## Task summary

| Metric | Count |
|--------|-------|
| **Total tasks** | 35 |
| **US1** | 5 (T014–T018) |
| **US2** | 2 (T019–T020) |
| **US3** | 11 (T011–T013, T021–T026) |
| **US4** | 3 (T007, T030, part of T033–T034) |
| **Setup/foundational/fixture/integration/polish** | 14 |

**User macro tasks mapped**: (1) T008–T010, (2) T011–T013, (3) T014–T020, (4) T021–T023, (5) T024–T026, (6) T027–T029, (7) T007/T030, (8) T031–T032, (9) T033–T035.
