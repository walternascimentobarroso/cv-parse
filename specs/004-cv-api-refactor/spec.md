# Feature Specification: CV Extraction API Refactor

**Feature Branch**: `004-cv-api-refactor`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: Refactor the current CV extraction API to improve architecture, scalability, and maintainability while preserving the current behavior (constants, dependency injection, structured logging, streaming, response validation, validation layer separation, MIME constants, extractor error handling, domain interface separation, Strategy pattern for extractors, updated tests). Non-goals: no API contract change, no new extraction features, no storage schema change.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Extract Preserved (Priority: P1)

As an API consumer, I upload a document (PDF or plain text) and receive extracted text and a stored record identifier. The request and response shape, status codes, and supported formats remain unchanged after the refactor.

**Why this priority**: Refactor must not break existing clients or behavior.

**Independent Test**: Call the existing upload/extract endpoint with a valid PDF and a valid TXT file; verify response fields (text, id, format) and storage behavior match current behavior.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** I POST a valid PDF to the extract endpoint, **Then** I receive 200 with `text`, `id`, and `format` and the record is stored with the same schema as today.
2. **Given** the service is running, **When** I POST a valid plain-text file to the extract endpoint, **Then** I receive 200 with extracted text and a stored id.
3. **Given** the service is running, **When** I send an unsupported content type or missing file, **Then** I receive the same error status and message style as today (e.g. 400 with a clear message).
4. **Given** the service is running, **When** I send a file that exceeds the maximum size, **Then** I receive 413 with a clear message.

---

### User Story 2 - Observability for Operations (Priority: P2)

As an operator, I need structured logs for upload attempts, extraction success, extraction failures, and validation errors so I can monitor and troubleshoot the service without changing the API.

**Why this priority**: Operations and debugging depend on consistent, centralized logging.

**Independent Test**: Trigger uploads (success, validation error, extraction failure) and verify logs contain the expected events in a consistent, machine-readable format.

**Acceptance Scenarios**:

1. **Given** a valid upload, **When** extraction succeeds, **Then** a success event is logged (e.g. upload identifier, outcome, relevant metadata).
2. **Given** an invalid upload (wrong type, missing file, or oversized), **When** the request is rejected, **Then** a validation-error event is logged with enough context to diagnose the issue.
3. **Given** a valid file that fails during extraction (e.g. corrupted PDF), **When** extraction fails, **Then** a failure event is logged with error details and no unhandled exception is exposed to the client beyond the existing error response.

---

### User Story 3 - Large File Handling (Priority: P2)

As an API consumer, I can upload large files within the configured size limit without the service exhausting memory. The service processes the file in a streaming or chunked manner instead of loading the entire file into memory at once.

**Why this priority**: Prevents outages and improves scalability for large documents.

**Independent Test**: Upload a file at or near the maximum allowed size and verify the service completes successfully and memory usage remains bounded (e.g. no full-file read into memory before processing).

**Acceptance Scenarios**:

1. **Given** a file at the maximum allowed size, **When** I upload it for extraction, **Then** the request completes successfully and the response is the same as for smaller files.
2. **Given** the service has a configured maximum size, **When** processing any uploaded file, **Then** the implementation does not load the entire file into memory in one go for processing (streaming or chunked approach is used).

---

### User Story 4 - Maintainable and Testable Codebase (Priority: P3)

As a developer, I work in a codebase where configuration and domain boundaries are clear: no magic strings for collection names or content types, dependencies are provided at application composition (dependency injection), validation lives outside HTTP handlers, and extraction behavior is pluggable by document type (strategy pattern). Domain contracts are defined in dedicated modules.

**Why this priority**: Enables safe evolution and testing without touching framework or infrastructure details in the wrong places.

**Independent Test**: Code review and tests confirm constants for collections and content types, thin HTTP layer, separate validation and extraction strategies, and tests that cover routes, validation, and extractors with injected dependencies.

**Acceptance Scenarios**:

1. **Given** the codebase, **When** I look for collection names or supported MIME types, **Then** they are defined as named constants, not raw strings in business or route code.
2. **Given** the application startup, **When** repositories and extractors are created, **Then** they are composed once (e.g. at startup) and supplied to the HTTP layer via dependency injection rather than via global or request.app state where avoidable.
3. **Given** an upload request, **When** validation runs, **Then** it is performed in a dedicated validation layer (service or validators), not inside the route handler logic.
4. **Given** a document to extract, **When** the system chooses how to extract, **Then** it uses a strategy (pluggable by type) rather than conditional branches on file type in one place.
5. **Given** API responses, **When** the service returns success or error payloads, **Then** response shapes are validated (e.g. via response models) so they stay consistent.

---

### Edge Cases

- What happens when the same file is uploaded concurrently? Behavior remains unchanged (each request produces its own record and response).
- How does the system handle a valid Content-Type but corrupted or unreadable file content? Extraction fails, error is logged, and the client receives a generic 500-style error response as today; no stack trace or internal detail is exposed.
- What happens when storage is temporarily unavailable? Behavior remains unchanged (failure is handled and surfaced as a server error to the client, with optional logging).
- How are empty files handled? Current behavior is preserved (e.g. empty text and empty id or defined empty response).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose the same HTTP API contract (paths, methods, request/response shapes, and status codes) as before the refactor.
- **FR-002**: The system MUST store extraction records in the same schema and under the same logical collection as today; no storage schema or collection layout change.
- **FR-003**: The system MUST use named constants for database collection names and for supported MIME/content types; magic strings for these MUST NOT appear in route or domain logic.
- **FR-004**: The system MUST compose repositories and extraction behavior at application startup and supply them to the HTTP layer via dependency injection; access via request.app.state for these MUST be minimized or removed where feasible.
- **FR-005**: The system MUST emit structured logs for: upload attempts, extraction success, extraction failures, and validation errors; logging MUST be centralized and reusable across modules.
- **FR-006**: The system MUST process uploaded files in a streaming or chunked manner so that large files within the configured size limit do not require loading the entire file into memory at once.
- **FR-007**: The system MUST validate API responses with a consistent schema (e.g. response models) so that success and error responses conform to a defined shape.
- **FR-008**: The system MUST perform upload validation (file presence, content type, size) in a dedicated validation layer (service or validators module), not inside the HTTP route handler.
- **FR-009**: The system MUST use a strategy (pluggable) pattern for extraction by document type; file-type selection MUST NOT be implemented as a single conditional chain in one place.
- **FR-010**: The system MUST define domain contracts (e.g. extraction interface) in dedicated interface modules, representing domain contracts only.
- **FR-011**: The system MUST capture and log extraction errors (e.g. PDF parsing failures); extraction MUST NOT leave errors unhandled or unlogged.
- **FR-012**: The system MUST NOT add new extraction formats or features; only refactor existing behavior and structure.
- **FR-013**: All existing behavior MUST be covered by tests; tests MUST be updated to align with dependency injection, new service/validation layers, and extraction strategies, and MUST remain passing with equivalent or improved coverage.

### Key Entities

- **Extraction record**: A stored document representing one extraction (filename, content type, size, extracted text, status, created time). Schema and semantics unchanged.
- **Upload request**: A single file upload with optional metadata (e.g. filename, content type). Validated before processing.
- **Extraction strategy**: A contract that, given content and type, returns extracted text; one strategy per supported document type (e.g. PDF, plain text).
- **Validation result**: Result of validating an upload (e.g. ok + file, or error + message); produced by the validation layer and consumed by the route or service.

## Assumptions

- The existing allowed content types (e.g. PDF, plain text) and size limits remain configurable via environment/settings; only the representation (constants vs raw strings) and where they are used change.
- "Streaming" means the implementation reads the upload in chunks or via a stream when processing, not that the HTTP API must use chunked transfer encoding for responses.
- Response models may be implemented using the same technology as today (e.g. Pydantic) but the spec does not mandate a specific technology; only that responses follow a consistent, validated schema.
- Tests may use mocks or fakes for repositories and extractors to satisfy dependency injection and strategy pattern.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All magic strings for database collection names and for supported MIME/content types are removed from route and domain logic; only named constants are used.
- **SC-002**: Clear separation exists between HTTP routes (thin), validation layer, domain interfaces, and infrastructure (repositories, extractors); documented or evident from structure.
- **SC-003**: Structured logging is implemented and used for upload attempts, extraction success, extraction failures, and validation errors; logs are centralized and reusable.
- **SC-004**: Large files (up to the configured maximum size) are processed without loading the full file into memory in one go; streaming or chunked handling is implemented.
- **SC-005**: Extraction behavior is implemented via a strategy (pluggable) pattern; no single conditional chain on file type in one place.
- **SC-006**: All tests are updated to reflect the refactored architecture (dependency injection, validation layer, strategies) and all tests pass with equivalent or improved coverage.
- **SC-007**: API contract (paths, methods, request/response shapes, status codes) and storage schema remain unchanged; no new extraction features are added.
