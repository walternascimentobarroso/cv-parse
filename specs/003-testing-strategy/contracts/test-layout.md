# Contract: Test Layout

**Feature**: 003-testing-strategy  
**Date**: 2026-03-11

## Purpose

All automated tests live under a single top-level directory. The layout mirrors the source architecture (api, domain, infra) so that tests are easy to find and each layer has a clear place.

## Directory structure

```text
tests/
├── conftest.py           # Shared fixtures (TestClient, in-memory repo, etc.)
├── domain/               # Unit tests for src/domain
│   ├── __init__.py
│   └── test_<module>.py  # e.g. test_extractor.py
├── api/                  # API tests for src/api (HTTP endpoints)
│   ├── __init__.py
│   └── test_<module>.py  # e.g. test_routes.py
└── infra/                # Integration tests for src/infra
    ├── __init__.py
    └── test_<module>.py  # e.g. test_storage.py
```

## Naming conventions

| Element       | Convention | Example |
|---------------|------------|---------|
| Test module   | `test_<source_module>.py` | `test_extractor.py`, `test_routes.py`, `test_storage.py` |
| Test function | `test_<behavior>` (pytest discovery) | `test_plain_text_extraction`, `test_health`, `test_extract_missing_file` |
| Fixtures      | In `conftest.py`; name reflects purpose | `client`, `in_memory_repo` |

## Layer mapping

| tests/ subdir | Source layer | Test type   | External deps |
|---------------|--------------|------------|---------------|
| **domain/**   | src/domain   | Unit       | None (no server, no real DB/network) |
| **api/**      | src/api      | API        | App with overridden deps (TestClient); no live server |
| **infra/**    | src/infra    | Integration| Real or test doubles (e.g. in-memory DB, temp dirs); documented setup |

## Rules

- New tests for a given layer MUST be added under `tests/<layer>/` in a `test_*.py` file.
- Shared fixtures used by more than one layer MUST live in `tests/conftest.py` or be imported from there. Layer-specific fixtures MAY live in `tests/<layer>/conftest.py`.
- The test tree MUST NOT add top-level categories beyond `domain`, `api`, `infra` (no `tests/unit/` or `tests/e2e/` unless they align with the three layers; mirror only).
