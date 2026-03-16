# Data Model: Soft Delete and Restore for Extractions

## Entities

### Extraction

Represents a single extraction record stored in MongoDB and exposed through the Extractions API.

**Key responsibilities**:

- Capture the extracted content and associated metadata.
- Track lifecycle timestamps for creation, updates, and soft deletion.
- Support a “soft deleted” state that hides the record from default queries while keeping it restorable.

**Fields** (incremental additions highlighted):

- `id` (string / ObjectId as string): unique identifier for the extraction (existing).
- `created_at` (datetime): timestamp when the extraction was created (existing).
- `updated_at` (datetime): timestamp of the last modification to the extraction (NEW behavior; may already exist in code but is required by this feature).
- `deleted_at` (Optional[datetime]): timestamp when the extraction was soft deleted; `null` when the extraction is active (NEW).
- Other domain-specific fields (e.g., source file, extracted text, status) remain unchanged.

## State Model

The `Extraction` entity supports two primary states with respect to deletion:

1. **Active**:
   - `deleted_at == null`
   - Visible in all default GET/list queries.
   - Allowed operations:
     - Soft delete → transition to Soft Deleted.
     - Force delete → permanent removal.

2. **Soft Deleted**:
   - `deleted_at != null`
   - Hidden from all default GET/list queries.
   - Allowed operations:
     - Restore → transition back to Active.
     - Force delete → permanent removal.

State transitions and timestamps:

- **Create Extraction**:
  - Set `created_at = now`.
  - Set `updated_at = now`.
  - Set `deleted_at = null`.

- **Soft Delete Extraction**:
  - Precondition: extraction exists and `deleted_at == null`.
  - Set `deleted_at = now`.
  - Set `updated_at = now`.

- **Restore Extraction**:
  - Precondition: extraction exists and `deleted_at != null`.
  - Set `deleted_at = null`.
  - Set `updated_at = now`.

- **Force Delete Extraction**:
  - Precondition: extraction exists (any state).
  - Remove document from MongoDB.

## Validation Rules

At the data model / schema level:

- `created_at` MUST always be present and represent a valid datetime.
- `updated_at` MUST always be present and represent a valid datetime.
- `deleted_at` MAY be null; when non-null, it MUST be a valid datetime.

At the behavior level:

- Soft delete MUST be idempotent with respect to “already soft deleted” records:
  - Either no-op with a clear outcome, or return a specific error; the chosen semantics will be enforced consistently in the repository and API.
- Restore MUST only succeed when `deleted_at` is non-null; otherwise, it MUST fail with an error indicating that the extraction is not deleted.
- Force delete MUST ensure that the document is removed so subsequent read or restore operations fail with “not found”.

## Query Semantics

Default queries for extractions (single and list) MUST:

- Filter by `deleted_at == null` so that soft deleted records are not returned.
- Apply this filter inside the repository layer so that all callers benefit from consistent semantics.

The data model does not introduce any alternative storage or “trash” collection; soft delete is represented solely through the `deleted_at` field on the primary `Extraction` document.

