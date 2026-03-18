# Quickstart: Extract Personal Information from CV

**Feature**: `007-extract-personal-info`  
**Date**: 2026-03-18

This guide explains how to work with the new `parsed_data.personal_info`
section in the CV extraction API.

## 1. Run the API

From the repository root:

```bash
cp .env.example .env   # if not already done
make install
make up
```

The API will be available at `http://localhost:8000`.

## 2. Submit a CV for Extraction

Use your preferred HTTP client to call the existing extraction endpoint (for
example, a POST to `/v1/cv/extract` – adjust to the actual path used in the
project).

Example with `curl`:

```bash
curl -X POST "http://localhost:8000/v1/cv/extract" \
  -F "file=@/path/to/cv.pdf"
```

The response now includes `parsed_data.personal_info` in addition to the
existing sections.

## 3. Inspect `parsed_data.personal_info`

Example response snippet:

```json
{
  "filename": "cv.pdf",
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

If a field cannot be confidently extracted or fails validation, its value will
be `null` (or omitted, depending on the final domain model), and the rest of
the response remains valid.

## 4. Development & Testing Notes

- Personal information extraction is implemented in the domain layer via a
  `PersonalInfo` entity and a `PersonalInfoExtractor` service.
- The existing extractor pipeline is extended to:
  - Obtain `raw_text` as usual.
  - Call `PersonalInfoExtractor` with `raw_text`.
  - Attach the resulting `personal_info` object to `parsed_data`.
- Unit tests cover:
  - Typical CVs with name, email, and links.
  - CVs missing email or summary.
  - CVs with multiple links and malformed emails/URLs.

## 5. Limitations

- No AI/LLM or advanced NLP is used; extraction is based on deterministic rules
  and simple heuristics.
- Heuristics (such as header detection and summary identification) are designed
  to be simple and may require future tuning based on real-world CV samples.

