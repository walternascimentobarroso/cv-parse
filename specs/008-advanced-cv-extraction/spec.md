# Feature Specification: Advanced Structured CV Extraction (Backward Compatible)

**Feature Branch**: `008-advanced-cv-extraction`  
**Created**: 2026-03-18  
**Status**: Draft  
**Input**: User description: Improve CV extraction depth and consistency (multi-role
experience, STAR-style text, skills categorization, contact and languages)
while preserving existing `parsed_data` contracts; deterministic extraction
only; no LLM; DDD-friendly modular extractors.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract every job experience, not only the first (Priority: P1)

A recruiter or ATS user uploads a CV with several positions. The system returns
structured experience entries for each distinct role (company, title, dates,
description), so downstream matching and timeline views are accurate.

**Why this priority**: Missing roles is the most visible failure of shallow
parsing and directly harms hiring decisions.

**Independent Test**: Process fixture CVs with two or more roles and assert
that the number and ordering of experience entries match the document, without
collapsing multiple roles into one block.

**Acceptance Scenarios**:

1. **Given** a CV with three roles under an Experience section, **When** it is
   parsed, **Then** `parsed_data` contains three experience entries with
   distinct company/role/date groupings where detectable.
2. **Given** a CV where roles are separated by date lines or company headers,
   **When** it is parsed, **Then** boundaries between roles are respected and
   descriptions attach to the correct role.

---

### User Story 2 - Readable descriptions from STAR-style bullets (Priority: P2)

A user uploads a CV written with Situation / Task / Action / Result labels.
The system produces a single coherent description per role and, where
possible, separates ongoing responsibilities from standout results.

**Why this priority**: STAR layouts are common in senior CVs; merging them
improves readability without losing content.

**Independent Test**: Feed synthetic STAR-structured text into the extractor and
assert merged description plus optional responsibility/achievement fields.

**Acceptance Scenarios**:

1. **Given** bullets labeled S/T/A/R under one role, **When** parsed, **Then**
   the role’s main narrative field contains the full text in readable order
   without dropping sections.
2. **Given** explicit Task/Action and Result blocks, **When** parsed, **Then**
   optional structured fields (e.g. responsibilities list, achievements) may be
   populated when heuristics confidently apply.

---

### User Story 3 - Richer profile and skills picture (Priority: P2)

A user expects summary, contact channels, languages, and split hard vs soft
skills to appear in the parsed payload so integrations can filter and display
them.

**Why this priority**: Unblocks contact enrichment, language-aware routing,
and skill-based search.

**Independent Test**: CVs with Languages, Soft Skills, and Summary sections
yield populated additive fields while legacy fields still parse.

**Acceptance Scenarios**:

1. **Given** a CV with email, phone, LinkedIn, personal site, and summary,
   **When** parsed, **Then** personal/contact-related additive fields are
   filled where detectable.
2. **Given** separate Hard Skills and Soft Skills sections, **When** parsed,
   **Then** categorized skill lists are populated without losing the legacy
   flat skills list contract.

---

### User Story 4 - No breaking change for existing consumers (Priority: P1)

An API consumer that already reads `parsed_data` continues to work without code
changes; new data is additive or backward-compatible.

**Why this priority**: Reduces rollout risk and matches product constraint.

**Independent Test**: Regression tests against documents that predated this
feature: every previously documented key and type expectation for legacy
sections still holds; new keys appear alongside.

**Acceptance Scenarios**:

1. **Given** a client that reads `parsed_data.experience[].company` and
   `parsed_data.skills` as a list of strings, **When** new parsing runs,
   **Then** those fields remain present and meaningful; new fields do not
   replace required legacy shapes.
2. **Given** `parsed_data.personal_info` from prior features (e.g. `full_name`,
   `github`), **When** enhanced parsing runs, **Then** those keys are not
   removed; new keys (e.g. `location`, `website`, `name`) may be added.

---

### Edge Cases

- CVs with overlapping or ambiguous section headers (e.g. “Profile” vs
  “Summary”).
- Multiple concurrent jobs or overlapping date ranges.
- STAR labels in non-English or abbreviated forms.
- Skills listed only as a single comma-separated block without section labels.
- Certifications as plain lines vs “Name — Issuer” patterns.
- Very short or non-standard CVs (single section, no clear structure).

## Requirements *(mandatory)*

### Functional Requirements

**Backward compatibility**

- **FR-001**: System MUST NOT remove or rename any `parsed_data` field or key
  path that existing specifications or consumers rely on (including
  `experience`, `education`, `skills`, `certifications`, `personal_info`, and
  nested keys such as `full_name`, `github`, `start_year` / `end_year` where
  already defined).
- **FR-002**: New structured data MUST be additive: new keys or optional fields
  on existing objects only; where a legacy field type cannot hold enriched data
  (e.g. certifications as strings vs objects), System MUST retain the legacy
  representation and MAY add a parallel enriched representation (name to be
  chosen at implementation time, documented in plan).

**Enriched experience**

- **FR-003**: System MUST detect and emit multiple experience entries when the
  CV text contains multiple distinct roles (e.g. company + role + date
  patterns), avoiding a single entry that concatenates all roles.
- **FR-004**: Each experience entry MUST continue to support legacy fields
  (`company`, `role`, `start_date`, `end_date`, `description`) and MAY add
  `location`, `responsibilities` (list), and `technologies` (list) when
  extractable.
- **FR-005**: When STAR-like structure is detected, System MUST merge content
  into the primary description field in deterministic order; System MAY
  additionally populate responsibilities (from Task/Action) and achievements
  (from Result) when segmentation is confident.

**Education**

- **FR-006**: Education entries MUST retain legacy fields (`institution`,
  `degree`, `start_year`, `end_year` as applicable) and MAY add `field`,
  `start_date`, `end_date` as string fields when extractable.

**Skills**

- **FR-007**: `parsed_data.skills` MUST remain a list of strings aggregating
  detected skills for backward compatibility.
- **FR-008**: System MUST add categorized skill data without breaking FR-007:
  either as sibling keys `hard_skills` and `soft_skills` at `parsed_data`
  level, or another additive layout documented in the technical plan, such
  that consumers that only read `skills` still receive a complete flat list.

**Certifications**

- **FR-009**: Legacy list-style certification output MUST be preserved where it
  exists today; System MAY add structured certification entries (name +
  optional issuer) under an additive key.

**Personal / contact**

- **FR-010**: `parsed_data.personal_info` MUST be extended additively with
  `location`, `website`, and `name` (or equivalent) where extractable, without
  removing `full_name`, `email`, `phone`, `linkedin`, `github`, or `summary`
  where those keys are already part of the contract.
- **FR-011**: System MUST extract personal website URLs (non-LinkedIn profile
  sites) when clearly identifiable, using deterministic rules.

**Languages**

- **FR-012**: System MUST add a `languages` array on `parsed_data` (additive),
  each item with `name` and optional `level`, when a languages section or
  equivalent is detected.

**Extraction approach**

- **FR-013**: All extraction enhancements MUST be deterministic (regex,
  section detection, keyword heuristics); System MUST NOT depend on LLMs or
  external NLP APIs for this feature.
- **FR-014**: Parsing logic MUST remain testable in isolation from PDF I/O
  (text-in, structured-out).

**Architecture (planning constraint)**

- **FR-015**: Design MUST keep parsing abstractions in the domain layer and
  concrete extractors in infrastructure, favoring new extractors and registry
  composition over breaking changes to stable modules where feasible.

### Key Entities

- **Parsed CV (`parsed_data`)**: Root structured output; legacy keys preserved;
  enriched with optional experience fields, language list, categorized skills,
  and extended personal info.
- **Experience entry**: One employment period; narrative + optional lists for
  responsibilities, technologies, achievements.
- **Language entry**: Spoken language name and optional proficiency level.
- **Certification (structured)**: Certification name and optional issuing
  organization.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For acceptance fixture CVs with N ≥ 2 explicit roles in the
  Experience section, at least 90% of fixtures yield N experience entries (or
  documented-equivalent when dates overlap), with no single entry swallowing
  all roles.
- **SC-002**: For fixture CVs with labeled STAR blocks, 100% of acceptance
  cases retain all STAR subsection text in the merged role description (no
  silent drops).
- **SC-003**: For fixture CVs with separate Hard/Soft skill sections, at least
  85% have non-empty both `hard_skills` and `soft_skills` (or chosen additive
  keys) while `skills` remains a non-empty superset when the CV lists skills.
- **SC-004**: All existing automated tests that assert legacy `parsed_data`
  shape continue to pass without changing assertions for legacy keys.
- **SC-005**: Stakeholders can verify on a small labeled set of real CVs that
  contact fields (email, phone, LinkedIn, site) and languages appear more
  often than before this feature, without manual correction.

## Assumptions

- “Real CV sample as fixture” in testing refers to anonymized or synthetic PDFs
  committed as test assets, respecting privacy.
- Parallel certification representation (string list vs structured list) is
  acceptable to consumers as long as legacy list behavior is unchanged.
- Optional field `achievements` on experience may be added in implementation
  if aligned with STAR “Result” extraction; not mandatory for MVP if spec
  consolidation in description suffices.

## Out of Scope

- LLM or cloud NLP integration.
- UI or API route changes beyond what is strictly required to return richer
  `parsed_data`.
- Guaranteed perfection on arbitrary CV layouts; goal is materially better
  coverage and consistency on common formats.
