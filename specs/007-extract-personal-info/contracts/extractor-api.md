# Contracts: CV Extractor – Personal Information

**Feature**: `007-extract-personal-info`  
**Date**: 2026-03-18

## Scope

This contract describes how the existing CV extraction API is extended to
include `parsed_data.personal_info` without breaking existing consumers.

## Request

No changes are required to request shape for this feature. The same endpoints
and payloads used to submit documents (for example, upload of `cv.pdf`) remain
valid.

## Response

### Before

Conceptual example of a previous response:

```json
{
  "filename": "cv.pdf",
  "raw_text": "...",
  "parsed_data": {
    "experience": [],
    "education": [],
    "skills": [],
    "certifications": []
  }
}
```

### After (with personal_info)

The response is extended with a new `personal_info` object inside
`parsed_data`:

```json
{
  "filename": "cv.pdf",
  "raw_text": "...",
  "parsed_data": {
    "personal_info": {
      "full_name": "Ada Lovelace",
      "email": "ada.lovelace@example.com",
      "phone": "+1 (555) 123-4567",
      "linkedin": "https://www.linkedin.com/in/adalovelace",
      "github": "https://github.com/adalovelace",
      "summary": "Software engineer with experience in distributed systems..."
    },
    "experience": [],
    "education": [],
    "skills": [],
    "certifications": []
  }
}
```

### Field Semantics

- `parsed_data.personal_info.full_name: string | null`
- `parsed_data.personal_info.email: string | null`
- `parsed_data.personal_info.phone: string | null`
- `parsed_data.personal_info.linkedin: string | null`
- `parsed_data.personal_info.github: string | null`
- `parsed_data.personal_info.summary: string | null`

All keys are present; values may be `null` if not confidently extracted or if
they fail validation.

### Backward Compatibility

- Existing fields under `parsed_data` (such as `experience`, `education`,
  `skills`, `certifications`) keep their previous shape and semantics.
- Clients that ignore `parsed_data.personal_info` will continue to work
  unchanged.
- New clients can safely rely on the presence of the `personal_info` key and
  treat `null` values as “not found”.

