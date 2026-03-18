# Feature Specification: Extract Personal Information from CV

**Feature Branch**: `007-extract-personal-info`  
**Created**: 2026-03-18  
**Status**: Draft  
**Input**: User description: "Add a new `personal_info` section inside `parsed_data` that extracts,
normalizes, and validates personal information from CVs (full name, email,
phone, LinkedIn, GitHub, and summary) using deterministic rules and heuristics,
without AI/LLM dependencies, and integrating with the existing extractor
pipeline."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Parse personal information from CV (Priority: P1)

A hiring system user submits a CV (PDF or supported document) and receives a
parsed CV payload where `parsed_data.personal_info` is populated with the
candidate's full name, email, optional phone, optional LinkedIn, optional
GitHub, and a short summary, while existing sections (`experience`,
`education`, `skills`, `certifications`) keep their current behavior.

**Why this priority**: Personal information is required to identify and contact
the candidate and is a prerequisite for almost all downstream workflows that
use parsed CVs.

**Independent Test**: Submit CVs through the existing extractor entrypoint and
assert that `parsed_data.personal_info` is present, correctly shaped, and
populated according to the rules, without modifying or breaking existing
sections.

**Acceptance Scenarios**:

1. **Given** a CV containing a full name on the first non-empty line, a valid
   email, and LinkedIn/GitHub URLs, **When** the CV is processed through the
   extractor pipeline, **Then** `parsed_data.personal_info` contains
   `full_name`, `email`, `linkedin`, and `github` with normalized values and
   other `parsed_data` sections remain unchanged.
2. **Given** a CV missing optional fields such as phone or GitHub,
   **When** the CV is processed, **Then** `parsed_data.personal_info` includes
   `full_name` and `email`, and missing optional fields are returned as `null`
   (or absent) without causing errors.

---

### User Story 2 - Validate and normalize personal information (Priority: P2)

As a system integrator, I want the personal information fields to be validated
and normalized so that downstream systems can rely on a consistent shape and
format without re-validating or guessing.

**Why this priority**: Validation and normalization reduce bugs in downstream
integrations and enable deterministic behavior in matching, search, and
analytics.

**Independent Test**: Provide sample CVs and direct unit tests that pass raw
text into the personal information extraction component and assert on the
normalized and validated outputs (e.g., lowercased email, normalized URLs,
phone format) without calling external services.

**Acceptance Scenarios**:

1. **Given** extracted raw values that include leading/trailing whitespace and
   mixed-case emails, **When** the personal information is processed,
   **Then** emails are trimmed and lowercased, URLs are normalized, and phone
   numbers follow the agreed normalization rules where possible.

---

### User Story 3 - Keep extractor pipeline backward compatible (Priority: P3)

As an API consumer of the existing CV extractor, I want the new personal
information extraction to integrate with the current pipeline without breaking
contract shape or behavior for existing fields so that I can adopt the new data
incrementally.

**Why this priority**: Backward compatibility reduces migration risk and
ensures existing consumers continue to work.

**Independent Test**: Run existing contract and integration tests for the
extractor alongside new tests and verify that previously returned sections keep
their shape and semantics while `parsed_data.personal_info` is added in a
backward-compatible way.

**Acceptance Scenarios**:

1. **Given** existing tests and clients that rely on current `parsed_data`
   structure, **When** the new feature is enabled, **Then** responses remain
   valid for those clients and only add `parsed_data.personal_info` without
   renaming or removing existing fields.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- CVs where the first non-empty line is not a name (for example, a job title or
  a header with contact information).
- CVs with multiple email addresses or multiple profile URLs (LinkedIn or
  GitHub) scattered across the document.
- CVs missing required fields (for example, email present but name not clearly
  identifiable or vice versa).
- CVs containing malformed emails or URLs that should be rejected as invalid
  rather than stored as-is.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST add a `personal_info` object inside
  `parsed_data` with the shape:
  `{"full_name": string|null, "email": string|null, "phone": string|null, "linkedin": string|null, "github": string|null, "summary": string|null}`.
- **FR-002**: System MUST extract `email` from the CV using deterministic
  regex-based rules and ignore clearly invalid email-like strings (for
  example, missing `@` or domain).
- **FR-003**: System MUST extract profile URLs for LinkedIn and GitHub
  using deterministic rules (for example, URL parsing and matching known
  host patterns) and normalize them to a canonical form.
- **FR-004**: System MUST extract `full_name` heuristically as the first
  non-empty line of the CV text while ignoring lines that are primarily
  emails, URLs, or obvious headers.
- **FR-005**: System MUST extract `summary` as the paragraph immediately
  below the name/contact block, typically containing a short biography
  or overview, without relying on AI/LLM or external NLP services.
- **FR-006**: System MUST treat `full_name` and `email` as required
  fields in the model (they MUST be present as keys in
  `parsed_data.personal_info`), but allow their values to be `null` if
  not confidently extracted.
- **FR-007**: System MUST validate `email` format (basic RFC-compliant
  shape) and MUST NOT return values that fail validation.
- **FR-008**: System MUST validate LinkedIn and GitHub URLs as syntactic
  URLs and as belonging to the expected domains (linkedin.com,
  github.com) before storing them; otherwise, it MUST treat them as
  not found.
- **FR-009**: System MUST return `null` (or omit the value) for any
  field that cannot be confidently extracted or that fails validation,
  without failing the overall extraction.
- **FR-010**: System MUST integrate the personal information extraction
  into the existing extractor pipeline without changing or removing
  existing `parsed_data` sections.
- **FR-011**: System MUST keep the personal information extraction
  logic testable in isolation (for example, as pure or side-effect-free
  functions where possible) so unit tests can run without PDF parsing or
  I/O.
- **FR-012**: System MUST avoid introducing any AI/LLM or external NLP
  dependencies for this feature, but MUST structure parsing logic so
  that AI-based strategies can be plugged in later behind stable
  interfaces.

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 95% of CVs with a clearly identifiable name and email
  result in non-null `full_name` and `email` in `parsed_data.personal_info`
  during acceptance testing.
- **SC-002**: At least 90% of valid LinkedIn and GitHub profile URLs present in
  sample CVs are correctly extracted and normalized.
- **SC-003**: Parsing personal information for a typical CV adds no more than
  50 ms to the existing extractor pipeline latency at p95 in test
  environments.
- **SC-004**: No existing API clients need to change their handling of current
  `parsed_data` fields to adopt the new `personal_info` section.
