# Quickstart: 008 Advanced CV Extraction

## Prerequisites

- `uv sync` (includes dev group `fpdf2` for regenerating `profile.pdf`).

## Run parser locally

```python
from src.domain.cv_parser import parse_cv

text = open("sample.txt").read()
data = parse_cv(text)
# data.hard_skills, data.soft_skills, data.languages, data.certification_details
# data.experience (multi-entry + STAR-merged descriptions when applicable)
```

## Regenerate golden PDF

```bash
uv run python tests/fixtures/build_profile_fixture.py
```

## Tests

```bash
uv run pytest tests/integration/test_full_cv_parsing.py -v
uv run pytest tests/domain/test_experience_enhanced.py tests/domain/test_skills_categorized.py tests/domain/test_languages_extractor.py -v
```

## Feature flag

- **`CV_PARSER_ENHANCED=false`** — use legacy `parse_experience_section` only (single-path dates on header line).
- Default: enhanced multi-line date merge + STAR.

## Logs

- **INFO**: `cv_parse_stage … elapsed_ms=…` per phase in `src/application/cv_parsing.py`.
- **DEBUG**: experience block count in `experience_extractor`.
