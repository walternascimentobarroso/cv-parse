# Data Model: Extract Personal Information from CV

**Feature**: `007-extract-personal-info`  
**Date**: 2026-03-18

## Overview

The feature introduces a new `personal_info` section inside `parsed_data` for
CV documents. The existing `parsed_data` structure remains unchanged; the
feature only adds a new nested object.

High-level shape:

```json
{
  "filename": "cv.pdf",
  "raw_text": "...",
  "parsed_data": {
    "personal_info": {
      "full_name": "",
      "email": "",
      "phone": "",
      "linkedin": "",
      "github": "",
      "summary": ""
    },
    "experience": [],
    "education": [],
    "skills": [],
    "certifications": []
  }
}
```

In practice, values may be `null` when not confidently extracted or when
validation fails, but keys are preserved.

## Entities

### 1. PersonalInfo (domain entity)

- **Represents**: Structured personal information extracted from a CV.
- **Location** (intended): `src/domain/personal_info/entities/personal_info.py`

#### Fields

- `full_name: str | None`
  - **Description**: Candidate’s full name as it appears on the CV header.
  - **Source**: Heuristic extraction from the first non-empty, non-contact line
    of the CV.
  - **Validation**:
    - Non-empty after trimming.
    - Should not be an email or URL.
  - **Constraints**:
    - Key is required in `parsed_data.personal_info`.
    - Value may be `null` if not confidently extracted.

- `email: str | None`
  - **Description**: Primary contact email.
  - **Source**: Deterministic regex-based extraction from the CV text (header
    block prioritized).
  - **Normalization**:
    - Trim whitespace.
    - Lowercase entire email.
  - **Validation**:
    - Shape must match a basic RFC-compliant email regex (local@domain.tld).
  - **Constraints**:
    - Key is required in `parsed_data.personal_info`.
    - Value may be `null` when no valid email is found.

- `phone: str | None`
  - **Description**: Primary contact phone number (if present).
  - **Source**: Regex/rule-based extraction from header block or entire text.
  - **Normalization**:
    - Trim whitespace.
    - Remove obvious formatting characters (spaces, hyphens, parentheses)
      where appropriate.
  - **Validation**:
    - Basic digit-count or pattern checks (e.g., minimum length).
  - **Constraints**:
    - Optional field; may be `null`.

- `linkedin: str | None`
  - **Description**: LinkedIn profile URL.
  - **Source**: URL extraction with host filter `linkedin.com`.
  - **Normalization**:
    - Ensure scheme (`https://`) present.
    - Normalize to a canonical host (e.g., `www.linkedin.com` vs
      `linkedin.com`).
  - **Validation**:
    - Must be a syntactically valid URL.
    - Host must match LinkedIn domains.
  - **Constraints**:
    - Optional field; may be `null`.

- `github: str | None`
  - **Description**: GitHub profile URL.
  - **Source**: URL extraction with host filter `github.com`.
  - **Normalization**:
    - Ensure scheme (`https://`) present.
  - **Validation**:
    - Must be a syntactically valid URL.
    - Host must be `github.com`.
  - **Constraints**:
    - Optional field; may be `null`.

- `summary: str | None`
  - **Description**: Short biography/about paragraph near the top of the CV.
  - **Source**: First non-empty paragraph after the header block containing the
    name/contact info.
  - **Normalization**:
    - Trim whitespace.
    - Optionally collapse excessive internal whitespace.
  - **Constraints**:
    - Optional field; may be `null`.

## Relationships

- `PersonalInfo` is **embedded** inside the larger CV document model under
  `parsed_data.personal_info`.
- The feature does not introduce new collections or external references; MongoDB
  documents remain compatible because of the flexible schema.

## Validation & State

- Validation runs as part of building a `PersonalInfo` instance:
  - Invalid emails/URLs cause the corresponding value to be set to `None`
    rather than raising errors.
  - The extraction pipeline may record non-fatal validation issues separately
    (implementation detail), but API responses remain structurally valid.
- `PersonalInfo` is effectively immutable once created in a single extraction
  run; subsequent pipeline stages treat it as read-only data.

## Mapping to API Responses

- API responses that expose CV data will include `parsed_data.personal_info`
  when available.
- No existing fields in `parsed_data` are renamed or removed; consumers that
  ignore `personal_info` will continue to work unchanged.

