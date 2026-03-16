# Feature Specification: Structured CV Parsing (without LLM)

**Feature Branch**: `006-structured-cv-parsing`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: User description: "Feature: Structured CV Parsing (without LLM). Transform raw CV text into structured data (work experience, education, skills, certifications) using deterministic parsing—section detection, heuristics, pattern matching. No LLM or external AI. Store structured data alongside raw text."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload CV and Receive Structured Data (Priority: P1)

A user uploads a CV document. The system extracts the raw text and then parses it into structured sections (experience, education, skills, certifications). The user receives a response that includes both the raw text and the structured parsed data, and both are stored for later use.

**Why this priority**: Core value of the feature—delivering structured CV data from an upload without requiring AI services.

**Independent Test**: Upload a CV with recognizable section headings; verify response includes parsed_data with at least one populated section and that the same data is persisted.

**Acceptance Scenarios**:

1. **Given** the user has a valid CV file, **When** they upload it, **Then** the system returns raw extracted text and structured parsed data (experience, education, skills, certifications).
2. **Given** a successful upload, **When** the user or system retrieves the CV record, **Then** both raw text and parsed data are available.
3. **Given** a CV with no recognizable sections, **When** it is parsed, **Then** structured sections are returned (possibly empty) and raw text is still stored.

---

### User Story 2 - Section Detection from Common Headings (Priority: P2)

The system identifies CV sections by recognizing common section headings (e.g. experience, education, skills, certifications and their variants). Content under each heading is assigned to that section until the next section header is found.

**Why this priority**: Section detection is the foundation for correct assignment of content to the right structured buckets.

**Independent Test**: Provide text with known section titles (e.g. "Work Experience", "Education"); verify content is split into the correct sections.

**Acceptance Scenarios**:

1. **Given** text containing headings such as "Experience", "Work Experience", "Professional Experience", "Employment", or "Career History", **When** parsed, **Then** the following content is assigned to the experience section until the next section.
2. **Given** equivalent headings for education, skills, and certifications (e.g. "Education", "Academic Background", "Skills", "Technical Skills", "Certifications", "Licenses", "Certificates"), **When** parsed, **Then** content is assigned to the corresponding sections.
3. **Given** text with no section headers, **When** parsed, **Then** all content may be unattributed or placed in a single/default section per product rules; parsing does not fail.

---

### User Story 3 - Structured Fields per Section (Priority: P3)

For each detected section, the system extracts structured fields where possible: for experience (e.g. company, role, dates, description), for education (e.g. institution, degree, years), for skills (matched from a defined list), and for certifications (certification names).

**Why this priority**: Enables downstream use (search, filtering, display) without depending on AI.

**Independent Test**: Provide CV text with clear experience/education/skills/certification content; verify parsed_data contains the expected field-level structure and reasonable values.

**Acceptance Scenarios**:

1. **Given** experience content with company name, role, and date-like text, **When** parsed, **Then** experience entries include company, role, start_date, end_date (when detectable), and description where applicable.
2. **Given** education content with institution and degree, **When** parsed, **Then** education entries include institution, degree, start_year, end_year (when detectable).
3. **Given** skills content and a predefined skills list, **When** parsed, **Then** skills are populated by matching keywords from that list.
4. **Given** certifications content, **When** parsed, **Then** certification names are captured in the certifications section.

---

### User Story 4 - Deterministic Parsing Only (Priority: P1)

Parsing uses only deterministic rules: section detection, pattern matching, and keyword matching. No LLM, no external AI, and no semantic NLP models are used.

**Why this priority**: Non-negotiable constraint that defines scope and guarantees predictable, reproducible behavior.

**Independent Test**: Verify that no outbound calls to AI/LLM services occur during parsing and that results are reproducible for the same input.

**Acceptance Scenarios**:

1. **Given** any CV input, **When** parsing runs, **Then** no LLM or external AI service is invoked.
2. **Given** the same raw text input run twice, **When** parsed, **Then** the structured output is identical.

---

### Edge Cases

- What happens when the CV has non-standard or non-English section headings? System should still store raw text; structured sections may be empty or partially filled based on detectable patterns.
- What happens when date or company/role patterns are ambiguous? System should extract what it can and leave other fields empty or best-effort; parsing does not fail.
- What happens when the same heading appears twice (e.g. two "Experience" sections)? Content after the second heading is assigned to that section; product may define whether to merge or keep separate entries.
- What happens when the uploaded file is not a valid CV or extraction yields empty or corrupt text? System should persist the record with empty or minimal parsed_data and a status that reflects the outcome; API response remains consistent in shape.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extract raw text from an uploaded CV document and persist it with the document record.
- **FR-002**: System MUST parse the raw text into structured sections: experience, education, skills, and certifications, using only deterministic rules (section detection, pattern matching, keyword matching).
- **FR-003**: System MUST recognize common section headings for experience (e.g. experience, work experience, professional experience, employment, career history), education (e.g. education, academic background, academic history), skills (e.g. skills, technical skills, core skills), and certifications (e.g. certifications, licenses, certificates), and assign content to the appropriate section until the next section header.
- **FR-004**: System MUST populate experience entries with structured fields where detectable: company, role, start_date, end_date, description.
- **FR-005**: System MUST populate education entries with structured fields where detectable: institution, degree, start_year, end_year.
- **FR-006**: System MUST extract skills using keyword matching against a predefined skills list.
- **FR-007**: System MUST capture certification names in the certifications section.
- **FR-008**: System MUST store with each CV record: filename, content type, size, raw text, parsed data (experience, education, skills, certifications), status, and created timestamp.
- **FR-009**: System MUST NOT use any LLM or external AI service for parsing; behavior MUST be deterministic and reproducible for the same input.
- **FR-010**: Parsing logic MUST be separated from API/transport layer so that parsing can be tested and evolved independently.

### Key Entities

- **CV document**: A stored record representing an uploaded CV. Key attributes: filename, content type, size, raw extracted text, parsed data (structured sections), status, created timestamp.
- **Parsed data**: Structured representation of the CV. Contains experience (list of entries with company, role, dates, description), education (list with institution, degree, years), skills (list matched from a predefined set), certifications (list of certification names).
- **Experience entry**: Single work experience item with company, role, start_date, end_date, description (when detectable).
- **Education entry**: Single education item with institution, degree, start_year, end_year (when detectable).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a user uploads a CV, the response includes both raw extracted text and structured parsed data (experience, education, skills, certifications) in a single round trip.
- **SC-002**: Stored CV records consistently contain raw text and parsed_data; retrieval returns the same structured shape.
- **SC-003**: Parsing produces identical structured output for the same raw text input when run multiple times (determinism).
- **SC-004**: Parsing completes without calling any LLM or external AI service; behavior is reproducible in offline or restricted environments.

## Assumptions

- The existing flow for PDF upload and raw text extraction remains in place; this feature adds a parsing step and extends the stored and returned data.
- "Predefined skills list" is maintained as configuration or data owned by the product; scope and source are defined during implementation.
- Date and field extraction are best-effort; partial or empty fields are acceptable when patterns are not detected.
- Section detection is line-based (scan line-by-line for headings); exact matching rules (e.g. case sensitivity, variants) are defined in implementation.
