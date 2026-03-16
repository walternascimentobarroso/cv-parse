# Tasks: Structured CV Parsing (without LLM)

**Input**: Design documents from `/specs/006-structured-cv-parsing/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: This feature benefits from focused unit and API tests; tasks below include explicit test work.  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- All descriptions include exact file paths.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm existing structures and identify integration points.

- [ ] T001 Inspect CV upload route and identify handler function in `src/api/routes.py`.
- [ ] T002 Inspect MongoDB CV repository implementation and confirm collection and document shape in `src/infra/mongo_cv_repository.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core structures that MUST exist before user stories can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Define `CvParsedData`, `ExperienceEntry`, and `EducationEntry` domain types in `src/domain/cv_parser.py` based on `specs/006-structured-cv-parsing/data-model.md`.
- [ ] T004 Extend CV document persistence to include `raw_text` and `parsed_data` fields in `src/infra/mongo_cv_repository.py`.
- [ ] T005 Update CV upload response model (or schema) to expose `raw_text` and `parsed_data` in `src/api/routes.py`.

**Checkpoint**: Domain types, persistence, and response shape ready for parsing integration.

---

## Phase 3: User Story 1 - Upload CV and Receive Structured Data (Priority: P1) 🎯 MVP

**Goal**: A user uploads a CV and receives both raw extracted text and structured parsed data, all stored in MongoDB.

**Independent Test**: Upload a CV with recognizable section headings; verify API response includes `raw_text` and `parsed_data` and that the stored document in MongoDB matches the same shape.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Implement `parse_cv(raw_text)` orchestrator in `src/domain/cv_parser.py` that coordinates section detection and per-section parsers to return `CvParsedData`.
- [ ] T007 [US1] Integrate `parse_cv` into the CV upload flow in `src/api/routes.py` (after text extraction, before persistence).
- [ ] T008 [US1] Persist `raw_text` and `parsed_data` for each uploaded CV using `mongo_cv_repository` in `src/infra/mongo_cv_repository.py`.
- [ ] T009 [P] [US1] Add API test covering upload → extract → parse → store flow in `tests/api/test_cv_upload_parsing.py`.

**Checkpoint**: Uploading a typical CV returns populated `parsed_data` and stores it alongside `raw_text`.

---

## Phase 4: User Story 2 - Section Detection from Common Headings (Priority: P2)

**Goal**: Reliably split raw CV text into sections using known headings for experience, education, skills, and certifications.

**Independent Test**: Given sample text with standard headings, `section_detector` returns correctly labeled sections; given text with no headings, parsing still succeeds with reasonable defaults.

### Implementation for User Story 2

- [ ] T010 [P] [US2] Implement heading lists and normalization rules for experience, education, skills, and certifications in `src/domain/section_detector.py`.
- [ ] T011 [US2] Implement `split_into_sections(raw_text: str) -> dict[str, str]` in `src/domain/section_detector.py` using line-by-line scanning and heading detection.
- [ ] T012 [P] [US2] Add unit tests for typical and edge-case headings in `tests/domain/test_section_detector.py`.

**Checkpoint**: `split_into_sections` is deterministic and well-tested for supported headings.

---

## Phase 5: User Story 3 - Structured Fields per Section (Priority: P3)

**Goal**: Extract structured fields for experience, education, skills, and certifications using deterministic heuristics.

**Independent Test**: Given section text samples, each parser returns the expected structured objects and lists, independent of the full upload flow.

### Implementation for User Story 3

- [ ] T013 [P] [US3] Implement experience parsing functions (e.g., `parse_experience_section(text: str) -> list[ExperienceEntry]`) in `src/domain/experience_parser.py` using role/company/date heuristics.
- [ ] T014 [P] [US3] Implement education parsing functions (e.g., `parse_education_section(text: str) -> list[EducationEntry]`) in `src/domain/education_parser.py` using institution/degree/year heuristics.
- [ ] T015 [P] [US3] Implement skills extraction functions (e.g., `extract_skills(text: str) -> list[str]`) using a predefined skills list in `src/domain/skills_extractor.py`.
- [ ] T016 [P] [US3] Implement certifications parsing functions (e.g., `parse_certifications_section(text: str) -> list[str]`) in `src/domain/certifications_parser.py`.
- [ ] T017 [US3] Wire per-section parsers into `parse_cv` in `src/domain/cv_parser.py` so that experience, education, skills, and certifications are all populated in `CvParsedData`.

### Tests for User Story 3

- [ ] T018 [P] [US3] Add unit tests for experience parsing heuristics in `tests/domain/test_experience_parser.py`.
- [ ] T019 [P] [US3] Add unit tests for education parsing heuristics in `tests/domain/test_education_parser.py`.
- [ ] T020 [P] [US3] Add unit tests for skills extraction with a sample skills dictionary in `tests/domain/test_skills_extractor.py`.
- [ ] T021 [P] [US3] Add unit tests for certifications parsing in `tests/domain/test_certifications_parser.py`.

**Checkpoint**: Given section text, each parser produces structured outputs consistent with the data model.

---

## Phase 6: User Story 4 - Deterministic Parsing Only (Priority: P1)

**Goal**: Guarantee that parsing uses only deterministic rules, with no LLMs or external AI services, and that output is stable for identical input.

**Independent Test**: Running `parse_cv` multiple times on the same raw text returns identical `parsed_data`, and no external network/AI calls occur during parsing.

### Implementation and Tests for User Story 4

- [ ] T022 [US4] Review `src/domain/section_detector.py`, `src/domain/experience_parser.py`, `src/domain/education_parser.py`, `src/domain/skills_extractor.py`, `src/domain/certifications_parser.py`, and `src/domain/cv_parser.py` to ensure no external network/AI dependencies or non-deterministic behavior.
- [ ] T023 [P] [US4] Add regression test verifying deterministic output for a fixed sample CV in `tests/domain/test_cv_parser_determinism.py`.
- [ ] T024 [US4] Add structured logging for parsing and extraction failures in `src/domain/cv_parser.py` and `src/api/routes.py` (e.g., log unexpected formats while keeping parsing best-effort).

**Checkpoint**: Determinism and non-AI constraints are enforced by tests and code review.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories once core behavior is in place.

- [ ] T025 [P] Update `specs/006-structured-cv-parsing/quickstart.md` with any implementation-specific details discovered during development.
- [ ] T026 Perform code cleanup and small refactors across new domain modules (`src/domain/*.py`) to maintain readability and single responsibility.
- [ ] T027 [P] Add additional unit tests for edge cases (e.g., missing dates, duplicate headings, non-standard layouts) in `tests/domain/`.
- [ ] T028 Run manual quickstart validation by uploading 2–3 real-world CV samples and verifying `parsed_data` against expectations.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion – BLOCKS all user stories.
- **User Stories (Phases 3–6)**: All depend on Foundational phase completion.
  - User Story 1 should be completed first as the MVP.
  - User Stories 2 and 3 can proceed in parallel after the foundational phase, as they focus on internal parsing behavior.
  - User Story 4 can proceed in parallel with 2 and 3 once initial implementations exist.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Setup and Foundational – provides end-to-end upload → parse → store behavior.
- **User Story 2 (P2)**: Depends on Foundational – `section_detector` can be implemented and tested independently of the full upload flow.
- **User Story 3 (P3)**: Depends on Foundational – per-section parsers can be implemented and tested using sample text.
- **User Story 4 (P1)**: Depends on initial implementations from User Stories 2 and 3 – validates determinism and non-AI constraints.

### Within Each User Story

- Prefer: unit tests written alongside implementation for each parser and orchestrator.
- Domain types and persistence (Phase 2) before API wiring (Phases 3 and 6).
- Orchestrator before full upload flow integration.
- Logging and determinism tests after core behavior works.

### Parallel Opportunities

- Tasks marked **[P]** can be executed in parallel:
  - Heading lists vs. split logic in section detection.
  - Separate parsers (experience, education, skills, certifications) and their tests.
  - API tests vs. domain tests once the upload flow is wired.
  - Documentation updates and additional edge-case tests during the Polish phase.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.  
2. Complete Phase 2: Foundational.  
3. Complete Phase 3: User Story 1 (upload → parse → store).  
4. **STOP and VALIDATE**: Verify API behavior and stored documents match the spec.  
5. Deploy/demo MVP if acceptable.

### Incremental Delivery

1. After MVP, implement User Story 2 (section detection) and validate independently.  
2. Implement User Story 3 (structured fields) and validate parsers via unit tests.  
3. Implement User Story 4 (determinism checks and logging) to enforce constraints.  
4. Complete Polish phase for documentation, additional tests, and minor refactors.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup and Foundational phases together.  
2. Then:
   - Developer A: User Story 1 (end-to-end wiring and API tests).  
   - Developer B: User Story 2 (section detection).  
   - Developer C: User Story 3 (per-section parsers and tests).  
   - Developer D: User Story 4 (determinism tests and logging) once parsers exist.  
3. Team jointly executes the Polish phase and quickstart validation.

