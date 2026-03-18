# Tasks: Extract Personal Information from CV

**Input**: Design documents from `/specs/007-extract-personal-info/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are explicitly requested in the feature description and spec (unit tests and edge cases), so test tasks are included per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (most already exists for this repo).

- [X] T001 Verify existing project environment setup using `make install` and `make up`
- [X] T002 [P] Confirm CV extraction pipeline entrypoint in `api/pipeline/extractor.py` and current `parsed_data` shape

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Define `parsed_data.personal_info` contract in `specs/007-extract-personal-info/contracts/extractor-api.md` (keep in sync with implementation)
- [X] T004 [P] Decide and document email and URL regex/validation rules in `specs/007-extract-personal-info/research.md`
- [X] T005 Ensure MongoDB document structure supports `parsed_data.personal_info` without schema migrations (validate against existing collection usage)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Parse personal information from CV (Priority: P1) 🎯 MVP

**Goal**: Populate `parsed_data.personal_info` (full_name, email, phone, linkedin, github, summary) from `raw_text` while keeping existing `parsed_data` sections unchanged.

**Independent Test**: Submit CVs through the existing extractor entrypoint and assert that `parsed_data.personal_info` is present, correctly shaped, and populated according to rules, without modifying or breaking existing sections.

### Tests for User Story 1 ⚠️

> Write these tests FIRST, ensure they FAIL before implementation.

- [X] T006 [P] [US1] Add unit tests for header parsing and personal info extraction in `tests/domain/personal_info/test_personal_info_extractor.py`
- [X] T007 [P] [US1] Add integration tests ensuring `parsed_data.personal_info` appears in API response in `tests/api/test_extractor_personal_info_integration.py`

### Implementation for User Story 1

- [X] T008 [P] [US1] Create `PersonalInfo` entity in `src/domain/personal_info/entities/personal_info.py`
- [X] T009 [P] [US1] Create `PersonalInfoExtractor` domain service skeleton in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T010 [US1] Implement header block detection and line splitting from `raw_text` in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T011 [US1] Implement email extraction (regex-based, deterministic) in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T012 [US1] Implement URL extraction for LinkedIn and GitHub (host-filtered) in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T013 [US1] Implement `full_name` heuristic (first non-empty non-contact line) in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T014 [US1] Implement summary paragraph extraction after header block in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T015 [US1] Map extracted fields into `PersonalInfo` and return a dictionary suitable for `parsed_data.personal_info` in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T016 [US1] Integrate `PersonalInfoExtractor` into main extractor pipeline in `api/pipeline/extractor.py` to inject `personal_info` into `parsed_data`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (personal_info present and populated for typical CVs, no regressions on other sections).

---

## Phase 4: User Story 2 - Validate and normalize personal information (Priority: P2)

**Goal**: Ensure all personal information fields are normalized and validated so downstream systems receive consistent, reliable data.

**Independent Test**: Use unit tests to pass raw values into `PersonalInfoExtractor` and assert normalized and validated outputs (lowercased email, normalized URLs, phone format) without external services.

### Tests for User Story 2 ⚠️

- [X] T017 [P] [US2] Extend unit tests to cover normalization (whitespace trimming, email lowercasing) in `tests/domain/personal_info/test_personal_info_extractor.py`
- [X] T018 [P] [US2] Add tests for URL validation and domain filtering (LinkedIn, GitHub) in `tests/domain/personal_info/test_personal_info_extractor.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement email normalization and validation rules in `src/domain/personal_info/entities/personal_info.py` or `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T020 [US2] Implement phone normalization and basic validation in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T021 [US2] Implement LinkedIn and GitHub URL normalization and domain checks in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T022 [US2] Ensure invalid emails/URLs result in `None` values rather than errors in `src/domain/personal_info/services/personal_info_extractor.py`
- [X] T023 [US2] Update `contracts/extractor-api.md` examples to reflect normalized values (lowercased email, canonical URLs)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently: extraction populates fields, and normalization/validation ensures consistent, trusted data.

---

## Phase 5: User Story 3 - Keep extractor pipeline backward compatible (Priority: P3)

**Goal**: Integrate personal information extraction without breaking existing API contracts or changing semantics of existing `parsed_data` sections.

**Independent Test**: Run existing contract and integration tests for the extractor alongside new tests and verify that previously returned sections keep their shape and semantics while `parsed_data.personal_info` is added.

### Tests for User Story 3 ⚠️

- [X] T024 [P] [US3] Add regression tests to ensure existing `parsed_data` fields remain unchanged when personal_info is added in `tests/api/test_extractor_personal_info_integration.py`

### Implementation for User Story 3

- [X] T025 [US3] Review `api/pipeline/extractor.py` to ensure `personal_info` is added without altering existing keys or types
- [X] T026 [US3] Verify MongoDB persistence and retrieval of documents with and without `personal_info` remain compatible in any repository or DAO modules (e.g. `src/infra/...` if applicable)
- [X] T027 [US3] Update any API schema/serialization layer (if present) to include `parsed_data.personal_info` while keeping previous fields intact

**Checkpoint**: All user stories should now be independently functional and backward compatible.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [ ] T028 [P] Update README with new `parsed_data.personal_info` example in `README.md`
- [X] T029 Add example response including `personal_info` to `specs/007-extract-personal-info/quickstart.md`
- [X] T030 Code cleanup and refactoring of `src/domain/personal_info/services/personal_info_extractor.py` for clarity and duplication removal
- [X] T031 [P] Add additional unit tests for tricky edge cases (missing email, multiple links, no summary) in `tests/domain/personal_info/test_personal_info_extractor.py`
- [ ] T032 Run full test suite (`make test`) and verify no regressions across features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User Story 1 (P1) should be implemented first (MVP).
  - User Story 2 (P2) builds on the extraction from User Story 1.
  - User Story 3 (P3) ensures compatibility after US1 and US2 are in place.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) – no dependencies on other stories.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) – depends on data structures and basic extraction from US1.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) – depends on US1 and US2 behaviors to verify compatibility.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation.
- Entity creation before services.
- Services before pipeline integration.
- Core implementation before integration and backward-compat checks.
- Story complete before moving to next priority.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- All Foundational tasks marked [P] can run in parallel (within Phase 2).
- Within each user story:
  - Unit tests and integration tests marked [P] can be created in parallel.
  - Independent parts of the extractor implementation (e.g., email vs URL extraction) can be split into separate subtasks if desired, provided they touch different functions.
- Different user stories can be worked on in parallel once their dependencies are satisfied (e.g., US2 normalization rules can proceed while US1 integration tests are being finalized).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories).
3. Complete Phase 3: User Story 1 (extraction only).
4. **STOP and VALIDATE**: Test User Story 1 independently via domain and API tests.
5. Expose the new `parsed_data.personal_info` to early consumers.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: personal_info present).
3. Add User Story 2 → Test independently → Deploy/Demo (normalized, validated fields).
4. Add User Story 3 → Test independently → Deploy/Demo (backward compatibility verified).
5. Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1 (extraction logic and basic integration).
   - Developer B: User Story 2 (normalization and validation rules).
   - Developer C: User Story 3 (backward compatibility tests and schema checks).
3. Stories complete and integrate independently; final polish phase aligns docs and edge-case coverage.

