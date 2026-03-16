# Tasks: Soft Delete and Restore for Extractions

**Input**: Design documents from `/specs/001-soft-delete-extractions/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: Tests are explicitly requested for this feature and are included per user story.  
**Organization**: Tasks are grouped by user story (US1–US3) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- All descriptions include exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm existing infrastructure and logging support needed for this feature.

- [X] T001 Verify extraction schemas and repository locations in `src/infra/schemas.py` and `src/infra/storage.py`
- [X] T002 Confirm logging configuration and logger usage patterns in `src/infra/logging_config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core pieces that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Ensure extraction Pydantic models in `src/infra/schemas.py` expose `created_at` and any existing timestamp fields
- [ ] T004 Introduce a shared helper for generating timezone-aware timestamps in an appropriate infra or domain utility file (for example, `src/infra/datetime_utils.py` or similar)
- [X] T005 Align repository interface for extractions in `src/infra/storage.py` with a single place where Mongo collection access is defined

**Checkpoint**: Foundation ready – user story implementation can now begin.

---

## Phase 3: User Story 1 – Soft delete an extraction without losing data (Priority: P1) 🎯 MVP

**Goal**: Allow clients to soft delete an extraction so it disappears from default queries while remaining restorable.

**Independent Test**: Call `DELETE /extractions/{id}` on an existing extraction, then verify via existing GET endpoints that the extraction no longer appears, while repository-level checks confirm the document still exists with `deleted_at` set.

### Tests for User Story 1

- [X] T006 [P] [US1] Add repository-level tests for soft delete behavior in `tests/infra/test_extraction_repository.py`
- [X] T007 [P] [US1] Add API tests for `DELETE /extractions/{id}` soft delete flow in `tests/api/test_extractions_soft_delete.py`

### Implementation for User Story 1

- [X] T008 [P] [US1] Add `updated_at` and `deleted_at` fields to the extraction schema in `src/infra/schemas.py`
- [X] T009 [US1] Implement `soft_delete` method on the extraction repository in `src/infra/storage.py` (set `deleted_at` and `updated_at` using a single update)
- [X] T010 [US1] Update repository read queries in `src/infra/storage.py` to filter extractions by `deleted_at == None` for all default get/list operations
- [X] T011 [US1] Implement `DELETE /extractions/{id}` route handler in `src/api/routes.py` that calls `soft_delete` and returns 204 or 404 on not found
- [X] T012 [US1] Add logging for soft delete operations (including extraction id) using the configured logger in `src/api/routes.py` or a shared logging helper
- [X] T013 [US1] Update any extraction response models in `src/infra/schemas.py` (and their usage in `src/api/routes.py`) to include `updated_at` and `deleted_at` fields where appropriate

**Checkpoint**: User Story 1 fully functional and testable independently (soft delete hides extractions from queries while keeping data).

---

## Phase 4: User Story 2 – Restore a previously soft deleted extraction (Priority: P1)

**Goal**: Allow clients to restore soft deleted extractions so they behave as active records again.

**Independent Test**: Soft delete an extraction, then call `POST /extractions/{id}/restore` and verify the extraction reappears in default GET endpoints with `deleted_at` cleared and `updated_at` advanced; attempting restore on a non-deleted extraction returns a 400 error.

### Tests for User Story 2

- [X] T014 [P] [US2] Add repository-level tests for restore behavior (only from soft deleted state) in `tests/infra/test_extraction_repository.py`
- [X] T015 [P] [US2] Add API tests for `POST /extractions/{id}/restore` happy-path and error cases in `tests/api/test_extractions_soft_delete.py`

### Implementation for User Story 2

- [X] T016 [US2] Implement `restore` method on the extraction repository in `src/infra/storage.py` that clears `deleted_at` and updates `updated_at` only when the record is soft deleted
- [X] T017 [US2] Implement `POST /extractions/{id}/restore` route handler in `src/api/routes.py` that calls `restore` and:
- [X] T018 [US2] Map “not found” restore results to HTTP 404 and “not deleted” restore attempts to HTTP 400 with a clear message in `src/api/routes.py`
- [X] T019 [US2] Ensure response models for restored extractions in `src/infra/schemas.py` and `src/api/routes.py` surface `updated_at` and `deleted_at` correctly (with `deleted_at` as `null` after restore)
- [X] T020 [US2] Add logging for restore operations (including extraction id and state change) using the project’s logger configuration

**Checkpoint**: User Story 2 fully functional and testable independently (restore works only from soft deleted state, with correct timestamps and errors).

---

## Phase 5: User Story 3 – Permanently remove an extraction when required (Priority: P2)

**Goal**: Allow clients to permanently delete extractions when needed so they no longer exist or can be restored.

**Independent Test**: Create an extraction (optionally soft delete it), then call `DELETE /extractions/{id}/force` and verify all subsequent GET or restore attempts fail with 404.

### Tests for User Story 3

- [X] T021 [P] [US3] Add repository-level tests for force delete behavior in `tests/infra/test_extraction_repository.py`
- [X] T022 [P] [US3] Add API tests for `DELETE /extractions/{id}/force` including non-existent id behavior in `tests/api/test_extractions_soft_delete.py`

### Implementation for User Story 3

- [X] T023 [US3] Implement `force_delete` method on the extraction repository in `src/infra/storage.py` that permanently removes the document by id regardless of `deleted_at`
- [X] T024 [US3] Implement `DELETE /extractions/{id}/force` route handler in `src/api/routes.py` that calls `force_delete` and returns 204 or 404 on not found
- [X] T025 [US3] Add logging for force delete operations (including extraction id) using the project’s logger configuration

**Checkpoint**: User Story 3 fully functional and testable independently (force delete permanently removes records and they cannot be restored).

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Ensure consistency, documentation, and cross-story quality.

- [X] T026 [P] Review all extraction-related response models in `src/infra/schemas.py` and `src/api/routes.py` for consistent inclusion of `created_at`, `updated_at`, and `deleted_at`
- [X] T027 [P] Ensure all extraction queries in `src/infra/storage.py` consistently apply `deleted_at == None` for default read paths
- [ ] T028 [P] Add or update developer-facing documentation in `specs/001-soft-delete-extractions/quickstart.md` if implementation details diverged from plan
- [X] T029 Run the full test suite relevant to extractions (`tests/api/` and `tests/infra/`) and address any regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion – blocks all user stories.
- **User Stories (Phases 3–5)**: All depend on Foundational phase completion.
  - US1 (soft delete) should be implemented first as MVP.
  - US2 (restore) depends logically on soft delete semantics being in place.
  - US3 (force delete) can be implemented after or in parallel with US2, once repository structure is stable.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2; no dependency on other stories.
- **User Story 2 (P1)**: Depends on User Story 1’s data model and repository structure.
- **User Story 3 (P2)**: Depends on foundational repository and API structure; behavior is independent of restore but benefits from having soft delete semantics established.

### Within Each User Story

- Tests for the story SHOULD be written and run alongside implementation, keeping them small and focused.
- Repository changes SHOULD be in place before adding or updating corresponding API routes.
- Logging and response model adjustments SHOULD follow once core behavior is working.

### Parallel Opportunities

- Tasks marked `[P]` can run in parallel:
  - T006–T007 (tests for US1) can be started in parallel once foundational work is ready.
  - Schema and repository tasks (T008–T010) can partially proceed in parallel where they touch different parts of the code.
  - API and test tasks per story (for example, T015 and T022) can be developed in parallel by different team members.
  - Polish tasks T026–T028 can run in parallel after core stories are complete.

