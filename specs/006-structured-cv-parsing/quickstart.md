## Quickstart: Structured CV Parsing (without LLM)

### 1. Where the code lives

- `src/api/routes.py`  
  - CV upload endpoint that receives the PDF, triggers text extraction, calls the CV parser, and stores the result.

- `src/domain/section_detector.py`  
- `src/domain/experience_parser.py`  
- `src/domain/education_parser.py`  
- `src/domain/skills_extractor.py`  
- `src/domain/cv_parser.py`  
  - Pure domain modules that implement deterministic parsing: section detection, per-section parsing, and orchestration.

- `src/infra/...`  
  - MongoDB repository that persists CV documents, extended to include `parsed_data`.

### 2. Running tests

- All tests:

```bash
uv run pytest tests/
```

- Domain-only tests for parsing:

```bash
uv run pytest tests/domain/
```

- API tests for upload + parse flow:

```bash
uv run pytest tests/api/
```

### 3. Happy-path development flow

1. Upload a sample CV via the existing upload endpoint.  
2. Verify that the response JSON includes `raw_text` and `parsed_data` with the four sections.  
3. Inspect the stored MongoDB document to confirm that `parsed_data` is persisted alongside the original metadata.

### 4. Extending parsing rules

- To refine section detection (e.g. new heading variants), update the heading lists in `section_detector.py`.  
- To improve experience or education extraction, adjust regexes and heuristics in their respective parser modules.  
- To add or refine skills, update the skills dictionary/config used by `skills_extractor.py`.  
- Keep changes small and covered by new unit tests in `tests/domain/`.

