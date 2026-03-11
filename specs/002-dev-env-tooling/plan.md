# Implementation Plan: Improve Development Environment and Project Tooling

**Branch**: `002-dev-env-tooling` | **Date**: 2025-03-11 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/002-dev-env-tooling/spec.md`

## Summary

Improve developer experience by replacing pip with uv as the Python package manager, introducing a single `.env` file for environment configuration, standardizing how the application and Docker Compose load variables, and adding a Makefile with `up`, `down`, and `logs` (and related) commands. Include a dependency lock strategy so installs are reproducible. Docker Compose reads from `.env` so app and containers share the same config. Aligns with constitution: minimal tooling surface, single responsibility (one package manager, one env source), explicit boundaries (documented commands and env contract).

## Technical Context

**Language/Version**: Python 3.12 (existing; from 001-doc-to-text-api)  
**Package manager**: uv (replacing pip); lockfile for reproducible installs  
**Primary Dependencies**: Unchanged from 001 (FastAPI, motor, pdfplumber, pydantic-settings, etc.); managed via uv and `pyproject.toml`  
**Environment**: Single `.env` at repo root; app loads via pydantic-settings (or equivalent); Docker Compose uses `env_file: .env`  
**Target Platform**: Local development (macOS/Linux) and Docker; same tooling used in CI where applicable  
**Project Type**: Dev tooling and project setup (no new application code; changes to tooling, config, and docs)  
**Constraints**: No new application features; only setup, package management, env loading, and developer commands  
**Scale/Scope**: Single repo; one Makefile, one `.env` template, one lockfile strategy

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Single-Responsibility**: Package management (uv), env config (.env), and command surface (Makefile) are separate concerns; each has one clear purpose.
- **YAGNI / Simplicity**: Only add tooling that the spec requires (uv, .env, Makefile with up/down/logs); no extra task runners or config systems.
- **Testable, Isolated**: Tooling changes do not add business logic; existing tests remain valid; lockfile and .env.example can be validated by scripts if needed.
- **Explicit Boundaries**: Env vars and Makefile targets are documented (contracts); app and Compose both consume the same env file.
- **Readability**: Makefile targets and .env variable names are descriptive; quickstart documents the workflow.
- **Clean Code constraints**: Limited scope (setup and DX only); minimal new dependencies (uv is the main addition); no premature optimization.

*Post–Phase 1*: Research resolves uv/lockfile and .env patterns; data-model and contracts document env entities and Makefile surface. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-dev-env-tooling/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1 (env config + command surface)
├── quickstart.md        # Phase 1 (developer setup guide)
├── contracts/           # Phase 1 (Makefile targets, .env vars)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

No new application modules. Changes are at repo root and in existing app config:

```text
# New or modified at repo root
.env.example             # Template of required/optional env vars (committed)
.env                     # Local overrides (gitignored)
Makefile                 # Targets: install, up, down, logs, etc.
pyproject.toml           # Project metadata + dependencies (replaces requirements.txt for uv)
uv.lock                  # Lockfile (committed) for reproducible installs

# Modified
docker-compose.yml       # env_file: .env; remove hardcoded env where appropriate
Dockerfile               # Use uv for install when building image
src/infra/config.py      # Load from env in a single, documented way (e.g. pydantic-settings)
```

**Structure Decision**: Tooling lives at repo root. Application continues to use `src/` and `tests/`; config loading is centralized in `src/infra/config.py` and reads from the environment (which is populated from `.env` locally or by Compose in containers).

## Complexity Tracking

No constitution violations requiring justification. One package manager (uv), one env file (`.env`), one command surface (Makefile).
