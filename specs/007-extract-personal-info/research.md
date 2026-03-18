# Research: Extract Personal Information from CV

**Feature**: `007-extract-personal-info`  
**Date**: 2026-03-18

## Decisions

### 1. Domain modeling for personal information

- **Decision**: Represent personal information as a dedicated `PersonalInfo`
  entity in the domain layer, with fields:
  `full_name`, `email`, `phone`, `linkedin`, `github`, `summary`, all optional
  at the value level but present as keys in `parsed_data.personal_info`.
- **Rationale**: A dedicated entity keeps responsibilities clear and aligns with
  the constitution’s Single-Responsibility and CV Parsing System Principles. It
  also makes validation and normalization logic reusable and testable in
  isolation.
- **Alternatives considered**:
  - Inline dictionary manipulation directly in the extractor pipeline
    (rejected: mixes formatting/validation concerns with orchestration).
  - Embedding personal info fields directly in the root of `parsed_data`
    (rejected: conflicts with the agreed structure and reduces cohesion).

### 2. Extraction strategy for email and URLs

- **Decision**: Use deterministic regex patterns for emails and simple URL
  parsing plus host checks for LinkedIn and GitHub URLs.
- **Rationale**: Regex and URL parsing are deterministic, fast, and easy to
  test. They satisfy the constitution’s requirement for deterministic extraction
  and avoid AI/LLM dependencies.
- **Alternatives considered**:
  - Heuristic or AI-based classifiers to identify contact lines
    (rejected for now: violates “no AI/LLM” constraint and adds complexity).
  - Very strict regexes that reject many real-world emails/URLs (rejected:
    would reduce recall too much).

### 3. Heuristic extraction for name and summary

- **Decision**: Extract the name as the first non-empty line of the document
  that is not primarily an email or URL; treat the “header block” as roughly
  the first 10 lines. Extract the summary as the first non-empty paragraph
  following this header block.
- **Rationale**: This reflects common CV layout conventions and keeps logic
  simple and explainable. It respects the constitution by using heuristics
  rather than AI, while remaining easy to adjust later.
- **Alternatives considered**:
  - Section-heading-based parsing (e.g., detecting “Summary”, “Profile”)
    (partially overlapped; can be added later as an enhancement without
    breaking the current contract).
  - Named-entity recognition via NLP libraries (rejected: adds heavyweight
    dependencies and drifts toward AI/LLM-like complexity).

### 4. Integration into existing extractor pipeline

- **Decision**: Integrate `PersonalInfoExtractor` as an early step in the
  existing extractor pipeline after raw text is available, adding
  `parsed_data.personal_info` to the existing `parsed_data` structure.
- **Rationale**: Keeps orchestration centralized, avoids duplicating parsing
  flows, and preserves backward compatibility by only extending the response.
- **Alternatives considered**:
  - A separate endpoint or pipeline only for personal info (rejected: adds
    maintenance overhead and diverges from current usage patterns).
  - Refactoring the entire pipeline in one step (rejected: too risky relative
    to feature scope).

### 5. Validation and normalization rules

- **Decision**: Apply normalization (trim whitespace, lowercase emails, normalize
  URLs, basic phone formatting) and validation (shape checks for email and
  URLs) inside the domain layer before returning `PersonalInfo`.
- **Rationale**: Centralizing this logic in the domain layer makes behavior
  consistent across all callers and satisfies the constitution’s requirement to
  validate at the domain boundary.
- **Alternatives considered**:
  - Performing validation at the API/controller level (rejected: spreads rules
    across layers and reduces reusability).
  - Storing raw values and leaving cleanup to consumers (rejected: leads to
    inconsistent behavior and violates the normalization requirement).

## Open Questions

No critical open questions remain for this feature; adjustments to heuristics
can be treated as future, backward-compatible refinements.

