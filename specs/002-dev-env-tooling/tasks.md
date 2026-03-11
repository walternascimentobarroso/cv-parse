# Tasks: Improve Development Environment and Project Tooling

**Input**: Design documents from `specs/002-dev-env-tooling/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in spec; no test tasks. Validation via quickstart run (Phase 6).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Repo root**: `pyproject.toml`, `Makefile`, `.env.example`, `docker-compose.yml`, `Dockerfile`
- **Application**: `src/infra/config.py` (existing)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Replace pip with uv; add pyproject.toml and lockfile; ensure .env is gitignored and .env.example is not.

- [x] T001 Create pyproject.toml at repo root with project name, version, Python 3.12, and dependencies from requirements.txt (fastapi, uvicorn[standard], motor, pdfplumber, pydantic-settings, pytest, httpx, ruff) per research.md
- [x] T002 [P] Ensure .env is gitignored and .env.example is not: in .gitignore keep .env and add !.env.example so .env.example can be committed
- [x] T003 Run uv lock at repo root to generate uv.lock; commit uv.lock for reproducible installs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Docker and env configuration so app and Compose can use the same config; app loads .env when present.

**⚠️ CRITICAL**: No user story work until this phase is complete

- [x] T004 Update Dockerfile at repo root to install dependencies with uv: install uv, COPY pyproject.toml uv.lock, run uv sync --frozen per research.md
- [x] T005 [P] Create .env.example at repo root with MONGODB_URI, MONGODB_DB, MAX_DOCUMENT_SIZE_BYTES, ALLOWED_CONTENT_TYPES and example values per specs/002-dev-env-tooling/contracts/env.md
- [x] T006 Update src/infra/config.py so Settings loads from .env when present (e.g. BaseSettings with env_file=".env") for local development per contracts/env.md

**Checkpoint**: Foundation ready; user story implementation can begin

---

## Phase 3: User Story 1 – One-Command Project Setup (Priority: P1) 🎯 MVP

**Goal**: Developer can clone, copy .env.example to .env, run make install, and run make up to get services running with minimal steps.

**Independent Test**: Clone repo, cp .env.example .env, make install, make up; then verify API and MongoDB are up (e.g. curl health or logs).

### Implementation for User Story 1

- [x] T007 [US1] Add Makefile at repo root with phony install target that runs uv sync per contracts/makefile.md
- [x] T008 [US1] Document one-command setup in specs/002-dev-env-tooling/quickstart.md: clone, cp .env.example .env, make install, make up; ensure quickstart reflects current flow

**Checkpoint**: User Story 1 is functional; new developer can follow quickstart to run services

---

## Phase 4: User Story 2 – Consistent Environment and Service Control (Priority: P2)

**Goal**: Developer uses make up, make down, make logs to control containerized services without remembering docker compose invocations.

**Independent Test**: Run make up, verify services start; run make logs and see output; run make down and verify containers stop.

### Implementation for User Story 2

- [x] T009 [P] [US2] Add Makefile target up (docker compose up -d) in Makefile at repo root per contracts/makefile.md
- [x] T010 [P] [US2] Add Makefile target down (docker compose down) in Makefile at repo root per contracts/makefile.md
- [x] T011 [P] [US2] Add Makefile target logs (docker compose logs -f) in Makefile at repo root per contracts/makefile.md
- [x] T012 [US2] Add optional Makefile targets run, test, lint in Makefile at repo root: run (uv run uvicorn with env from .env), test (uv run pytest), lint (uv run ruff check .) per contracts/makefile.md

**Checkpoint**: User Stories 1 and 2 both work; make up, make down, make logs are available

---

## Phase 5: User Story 3 – Standardized Environment Variable Loading (Priority: P3)

**Goal**: App and Docker Compose both read from the same .env; behavior is documented so developers know how config is loaded.

**Independent Test**: Set a variable in .env, start app via make run or make up; confirm app and containers see the same variable.

### Implementation for User Story 3

- [x] T013 [US3] Update docker-compose.yml at repo root: add env_file: .env for api service; remove or reduce hardcoded environment entries that duplicate .env variables per research.md and contracts/env.md
- [x] T014 [US3] Document env loading (app loads via pydantic-settings from .env; Compose uses env_file: .env) in specs/002-dev-env-tooling/quickstart.md and reference contracts/env.md

**Checkpoint**: All user stories are satisfied; env is single source for app and Compose

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Project documentation and validation; remove pip/requirements.txt from default path.

- [x] T015 [P] Update project documentation: add or update README at repo root with prerequisites (uv, Docker), setup steps (cp .env.example .env, make install, make up), list of Makefile targets (install, up, down, logs, run, test, lint), and link to specs/002-dev-env-tooling/quickstart.md
- [x] T016 [P] Remove requirements.txt from repo root (dependencies now in pyproject.toml and uv.lock); document in README that install uses uv only per FR-001
- [ ] T017 Run quickstart validation: follow specs/002-dev-env-tooling/quickstart.md from a clean state (make install, make up, make down, make logs) and verify all steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (pyproject.toml, uv.lock, .env.example); BLOCKS all user stories
- **User Stories (Phase 3–5)**: Depend on Phase 2; US1 then US2 then US3 in order (Makefile grows incrementally)
- **Polish (Phase 6)**: Depends on Phase 5 completion

### User Story Dependencies

- **US1 (P1)**: After Phase 2 only; delivers install target and setup docs
- **US2 (P2)**: After US1; adds up, down, logs (and optional run, test, lint) to same Makefile
- **US3 (P3)**: After Phase 2; can be done in parallel with US1/US2; Compose env_file and env-loading docs

### Within Each User Story

- US1: Makefile install before documenting setup (T007 before T008)
- US2: up, down, logs can be added in any order (T009–T011 [P]); T012 depends on Makefile existing
- US3: docker-compose.yml change (T013) before or with doc update (T014)

### Parallel Opportunities

- Phase 1: T002 [P] can run in parallel with T001 (different files: .gitignore vs pyproject.toml); T003 must follow T001
- Phase 2: T005 [P] (.env.example) can run in parallel with T004 (Dockerfile) and T006 (config.py)
- Phase 4: T009, T010, T011 [P] are independent (same Makefile but different targets; can be done in one edit)
- Phase 6: T015 and T016 [P] can run in parallel

---

## Parallel Example: Phase 2

```bash
# After T001–T003 complete, run in parallel:
Task T004: "Update Dockerfile to use uv"
Task T005: "Create .env.example"
Task T006: "Update config.py to load .env"
```

---

## Parallel Example: User Story 2

```bash
# Add all three required Makefile targets in one pass or in parallel:
Task T009: "Add Makefile target up"
Task T010: "Add Makefile target down"
Task T011: "Add Makefile target logs"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (pyproject.toml, uv.lock, .gitignore)
2. Complete Phase 2: Foundational (Dockerfile, .env.example, config.py)
3. Complete Phase 3: User Story 1 (Makefile install, quickstart)
4. **STOP and VALIDATE**: Follow quickstart; run make install, make up; verify services start
5. Optionally add US2 (up, down, logs) for daily use

### Incremental Delivery

1. Phase 1 + 2 → uv and env in place; Docker builds with uv; .env.example exists
2. Phase 3 (US1) → make install and documented setup (MVP for “one-command setup”)
3. Phase 4 (US2) → make up, make down, make logs
4. Phase 5 (US3) → Compose reads .env; env loading documented
5. Phase 6 → README and quickstart validation; remove requirements.txt

### Suggested Order for Single Developer

1. T001 → T002 → T003 (Setup)
2. T004, T005, T006 (Foundational; T005 and T006 can be parallel)
3. T007, T008 (US1)
4. T009, T010, T011, T012 (US2; one Makefile update)
5. T013, T014 (US3)
6. T015, T016, T017 (Polish)

---

## Notes

- [P] tasks = different files or independent edits; T009–T011 can be one Makefile edit
- [Story] label maps task to spec user story for traceability
- No application tests added; existing tests remain; validation is manual via quickstart (T017)
- Commit after each task or logical group (e.g. all Makefile targets together)
- .env.example must not be matched by .env.* in .gitignore (T002)
