# Feature Specification: Soft Delete and Restore for Extractions

**Feature Branch**: `001-soft-delete-extractions`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: Add soft delete and restore capabilities to the Extractions API, so that extractions are hidden by default but can be restored or permanently removed when required.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Soft delete an extraction without losing data (Priority: P1)

As a consumer of the Extractions API, I want to mark an extraction as deleted without permanently removing it, so that it no longer appears in normal queries but can still be restored if needed.

**Why this priority**: Preventing accidental data loss while keeping the API behavior intuitive for consumers is critical for safety and trust.

**Independent Test**: Can be fully tested by calling the soft delete endpoint on an existing extraction and verifying that it disappears from all default retrieval endpoints while remaining restorable.

**Acceptance Scenarios**:

1. **Given** an existing extraction that is not deleted, **When** the client sends a soft delete request for its identifier, **Then** the system marks the extraction as deleted and records the deletion time.
2. **Given** a soft deleted extraction, **When** any default GET endpoint is used to list or fetch extractions, **Then** that extraction is not included in the response.

---

### User Story 2 - Restore a previously soft deleted extraction (Priority: P1)

As a consumer of the Extractions API, I want to restore a soft deleted extraction so that it behaves like an active extraction again and appears in normal queries.

**Why this priority**: The ability to undo deletions is essential for correcting mistakes and supporting operational workflows.

**Independent Test**: Can be fully tested by soft deleting an extraction, restoring it via the restore endpoint, and verifying that it reappears in default retrieval endpoints with updated timestamps.

**Acceptance Scenarios**:

1. **Given** a soft deleted extraction, **When** the client sends a restore request for its identifier, **Then** the system clears the deletion time, updates the last-updated time, and the extraction becomes visible in default GET queries.
2. **Given** an extraction that is not soft deleted, **When** the client sends a restore request for its identifier, **Then** the system returns an error indicating that the extraction is not deleted and makes no changes.

---

### User Story 3 - Permanently remove an extraction when required (Priority: P2)

As a consumer of the Extractions API, I want to permanently remove an extraction in exceptional cases so that it no longer exists in the system and cannot be restored.

**Why this priority**: Some scenarios require complete removal of data (for example, testing data or records created in error), and the system must support explicit, irreversible deletion.

**Independent Test**: Can be fully tested by creating an extraction, optionally soft deleting it, performing a force delete, and verifying that subsequent retrieval or restore attempts for that identifier fail.

**Acceptance Scenarios**:

1. **Given** an extraction (whether active or soft deleted), **When** the client sends a force delete request for its identifier, **Then** the system permanently removes the extraction so that it no longer exists in the data store.
2. **Given** a non-existent extraction identifier, **When** the client sends a force delete request for that identifier, **Then** the system returns a not-found error and makes no changes.

---

### Edge Cases

- Soft deleting an extraction that does not exist: the system returns a not-found error and does not create any new record.
- Soft deleting an extraction that is already soft deleted: the system is idempotent (returns success without changing the deletion timestamp) or returns a clear error, but in all cases does not create duplicates.
- Restoring an extraction that does not exist: the system returns a not-found error.
- Restoring an extraction that is not soft deleted: the system returns an error indicating that the extraction is not deleted and does not modify timestamps.
- Forcing deletion of an extraction that has already been forcibly deleted or never existed: the system returns a not-found error and does not modify any data.
- Concurrent soft delete and restore requests for the same extraction: the system applies a deterministic outcome per request ordering, ensuring that the final state and timestamps are consistent and there is no partial update.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a soft delete operation for extractions that, when invoked for an existing active extraction identifier, sets a deletion timestamp while keeping the extraction data available for potential restoration.
- **FR-002**: The system MUST ensure that all default GET operations for extractions (single and list) exclude any extraction whose deletion timestamp is set.
- **FR-003**: The system MUST provide a restore operation for extractions that, when invoked for an existing soft deleted extraction, clears the deletion timestamp, updates the last-updated timestamp, and returns the extraction as active.
- **FR-004**: The system MUST prevent restore operations on extractions that are not soft deleted by returning an appropriate error and leaving all timestamps unchanged.
- **FR-005**: The system MUST support a force delete operation that permanently removes an extraction identified by its identifier, regardless of whether it is currently active or soft deleted.
- **FR-006**: The system MUST ensure that after a successful force delete, the targeted extraction cannot be returned by any retrieval operation and cannot be restored.
- **FR-007**: The system MUST expose timestamp fields for extractions that include creation time, last-updated time, and an optional deletion time that is set only when an extraction is soft deleted.
- **FR-008**: The system MUST ensure that all supported operations on extractions (soft delete, restore, and force delete) return clear error responses when the specified extraction identifier does not correspond to any existing record.
- **FR-009**: The system MUST keep the behavior of the Extractions API consistent across all entry points so that soft deleted extractions are treated as deleted for all default consumer-facing queries.

### Key Entities *(include if feature involves data)*

- **Extraction**: Represents a single extracted document or record, including its business attributes, a unique identifier, a creation timestamp, a last-updated timestamp, and an optional deletion timestamp used to indicate soft deletion.
- **Soft Deleted Extraction**: A conceptual state of an extraction where the deletion timestamp is set, meaning it is hidden from default queries and treated as deleted, but the underlying data remains available for potential restoration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In test environments, 100% of extractions that are soft deleted no longer appear in any default GET responses while remaining restorable via the restore operation.
- **SC-002**: In test environments, 100% of extractions that are soft deleted and then restored reappear in default GET responses with a more recent last-updated timestamp and a cleared deletion timestamp.
- **SC-003**: In test environments, 100% of extractions that are forcibly deleted cannot be retrieved or restored by any available operation.
- **SC-004**: For all tested Extractions API flows, soft delete, restore, and force delete operations return clear, documented error responses for non-existent or invalid identifiers, with no inconsistent or partial states observed.

# Feature Specification: Soft Delete and Restore for Extractions

**Feature Branch**: `001-soft-delete-extractions`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: Add soft delete and restore capabilities to the Extractions API, so that extractions are hidden by default but can be restored or permanently removed when required.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Soft delete an extraction without losing data (Priority: P1)

As a consumer of the Extractions API, I want to mark an extraction as deleted without permanently removing it, so that it no longer appears in normal queries but can still be restored if needed.

**Why this priority**: Preventing accidental data loss while keeping the API behavior intuitive for consumers is critical for safety and trust.

**Independent Test**: Can be fully tested by calling the soft delete endpoint on an existing extraction and verifying that it disappears from all default retrieval endpoints while remaining restorable.

**Acceptance Scenarios**:

1. **Given** an existing extraction that is not deleted, **When** the client sends a soft delete request for its identifier, **Then** the system marks the extraction as deleted and records the deletion time.
2. **Given** a soft deleted extraction, **When** any default GET endpoint is used to list or fetch extractions, **Then** that extraction is not included in the response.

---

### User Story 2 - Restore a previously soft deleted extraction (Priority: P1)

As a consumer of the Extractions API, I want to restore a soft deleted extraction so that it behaves like an active extraction again and appears in normal queries.

**Why this priority**: The ability to undo deletions is essential for correcting mistakes and supporting operational workflows.

**Independent Test**: Can be fully tested by soft deleting an extraction, restoring it via the restore endpoint, and verifying that it reappears in default retrieval endpoints with updated timestamps.

**Acceptance Scenarios**:

1. **Given** a soft deleted extraction, **When** the client sends a restore request for its identifier, **Then** the system clears the deletion time, updates the last-updated time, and the extraction becomes visible in default GET queries.
2. **Given** an extraction that is not soft deleted, **When** the client sends a restore request for its identifier, **Then** the system returns an error indicating that the extraction is not deleted and makes no changes.

---

### User Story 3 - Permanently remove an extraction when required (Priority: P2)

As a consumer of the Extractions API, I want to permanently remove an extraction in exceptional cases so that it no longer exists in the system and cannot be restored.

**Why this priority**: Some scenarios require complete removal of data (for example, testing data or records created in error), and the system must support explicit, irreversible deletion.

**Independent Test**: Can be fully tested by creating an extraction, optionally soft deleting it, performing a force delete, and verifying that subsequent retrieval or restore attempts for that identifier fail.

**Acceptance Scenarios**:

1. **Given** an extraction (whether active or soft deleted), **When** the client sends a force delete request for its identifier, **Then** the system permanently removes the extraction so that it no longer exists in the data store.
2. **Given** a non-existent extraction identifier, **When** the client sends a force delete request for that identifier, **Then** the system returns a not-found error and makes no changes.

---

### Edge Cases

- Soft deleting an extraction that does not exist: the system returns a not-found error and does not create any new record.
- Soft deleting an extraction that is already soft deleted: the system is idempotent (returns success without changing the deletion timestamp) or returns a clear error, but in all cases does not create duplicates.
- Restoring an extraction that does not exist: the system returns a not-found error.
- Restoring an extraction that is not soft deleted: the system returns an error indicating that the extraction is not deleted and does not modify timestamps.
- Forcing deletion of an extraction that has already been forcibly deleted or never existed: the system returns a not-found error and does not modify any data.
- Concurrent soft delete and restore requests for the same extraction: the system applies a deterministic outcome per request ordering, ensuring that the final state and timestamps are consistent and there is no partial update.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a soft delete operation for extractions that, when invoked for an existing active extraction identifier, sets a deletion timestamp while keeping the extraction data available for potential restoration.
- **FR-002**: The system MUST ensure that all default GET operations for extractions (single and list) exclude any extraction whose deletion timestamp is set.
- **FR-003**: The system MUST provide a restore operation for extractions that, when invoked for an existing soft deleted extraction, clears the deletion timestamp, updates the last-updated timestamp, and returns the extraction as active.
- **FR-004**: The system MUST prevent restore operations on extractions that are not soft deleted by returning an appropriate error and leaving all timestamps unchanged.
- **FR-005**: The system MUST support a force delete operation that permanently removes an extraction identified by its identifier, regardless of whether it is currently active or soft deleted.
- **FR-006**: The system MUST ensure that after a successful force delete, the targeted extraction cannot be returned by any retrieval operation and cannot be restored.
- **FR-007**: The system MUST expose timestamp fields for extractions that include creation time, last-updated time, and an optional deletion time that is set only when an extraction is soft deleted.
- **FR-008**: The system MUST ensure that all supported operations on extractions (soft delete, restore, and force delete) return clear error responses when the specified extraction identifier does not correspond to any existing record.
- **FR-009**: The system MUST keep the behavior of the Extractions API consistent across all entry points so that soft deleted extractions are treated as deleted for all default consumer-facing queries.

### Key Entities *(include if feature involves data)*

- **Extraction**: Represents a single extracted document or record, including its business attributes, a unique identifier, a creation timestamp, a last-updated timestamp, and an optional deletion timestamp used to indicate soft deletion.
- **Soft Deleted Extraction**: A conceptual state of an extraction where the deletion timestamp is set, meaning it is hidden from default queries and treated as deleted, but the underlying data remains available for potential restoration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In test environments, 100% of extractions that are soft deleted no longer appear in any default GET responses while remaining restorable via the restore operation.
- **SC-002**: In test environments, 100% of extractions that are soft deleted and then restored reappear in default GET responses with a more recent last-updated timestamp and a cleared deletion timestamp.
- **SC-003**: In test environments, 100% of extractions that are forcibly deleted cannot be retrieved or restored by any available operation.
- **SC-004**: For all tested Extractions API flows, soft delete, restore, and force delete operations return clear, documented error responses for non-existent or invalid identifiers, with no inconsistent or partial states observed.

# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

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

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
