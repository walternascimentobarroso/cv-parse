# Research: CV Extraction API Refactor (004-cv-api-refactor)

All technical context is known from the existing codebase; no NEEDS CLARIFICATION remained. This document records decisions and rationale for the refactor design.

---

## 1. Streaming / chunked upload handling (FastAPI)

**Decision**: Use FastAPI’s `UploadFile` and iterate over chunks via `file.iter_chunks()` (or equivalent) for size checking and for passing data to extraction, so the route never calls `file.read()` to load the entire file into memory at once.

**Rationale**: `UploadFile` is a wrapper over SpooledTemporaryFile; iterating chunks keeps memory bounded. For PDF and plain-text extractors that need full content, we can accumulate chunks in a buffer up to the configured max size and then pass the buffer to the strategy. This satisfies “do not load entire file in one go” at the route level; the extractor may still need full bytes for parsing (e.g. pdfplumber).

**Alternatives considered**: (a) Read full file into memory — rejected to meet FR-006 / SC-004. (b) Stream directly into a temp file and pass file path to extractors — adds file I/O and path handling; chunked buffer is simpler for current two-format support.

---

## 2. Structured logging format

**Decision**: Use Python’s standard `logging` with a formatter that emits key-value or JSON lines (e.g. `logging.config.dictConfig` with a JSON formatter or a custom Formatter). Log events with consistent fields: e.g. `event`, `message`, `content_type`, `filename`, `size_bytes`, `record_id`, `error`, `duration_ms`.

**Rationale**: Structured logs are required for operations (FR-005, SC-003). Standard library avoids new dependencies. JSON or key-value lines are easy to parse in log aggregators.

**Alternatives considered**: (a) Plain format strings — not machine-parseable. (b) Third-party (e.g. structlog) — adds dependency; not needed for current scope (constitution: minimal dependencies).

---

## 3. Strategy pattern: Protocol vs ABC

**Decision**: Use a `typing.Protocol` in `domain/interfaces.py` for the extractor strategy (e.g. `DocumentExtractorStrategy` with `extract(self, content: bytes) -> str`). Implementations live in `infra/extractors/`. A registry (map content_type → strategy) is the injectable “extractor” used by the app.

**Rationale**: Protocol allows structural subtyping and keeps domain free of implementation; no new base class in domain. Aligns with “domain interfaces in dedicated modules” (FR-010) and “strategy pattern” (FR-009).

**Alternatives considered**: (a) Abstract base class (ABC) in domain — would require domain to depend on a concrete method signature; Protocol is lighter and stays interface-only. (b) Single class with conditionals — explicitly forbidden by spec (FR-009).

---

## 4. Validation result type

**Decision**: Validation returns a small result type: either success (with file metadata and optionally the chunked iterator or buffer) or failure (with an error code and message string). The route maps failure to the same HTTP status and message style as today (400 for validation, 413 for size).

**Rationale**: Keeps validation layer free of HTTP (FR-008); route remains the only place that raises HTTP exceptions or builds HTTP responses.

**Alternatives considered**: Validator raising HTTPException — would couple validation to FastAPI; rejected.

---

## 5. Dependency injection mechanism

**Decision**: Use FastAPI’s `Depends()` with provider functions (e.g. `get_repo`, `get_extractor`) that return the instance stored on `app.state` during lifespan. Routes declare these as dependencies and do not read `app.state` directly.

**Rationale**: Standard FastAPI pattern; testable via `app.dependency_overrides`. Meets FR-004 (compose at startup, supply via DI; minimize request.app.state in route code).

**Alternatives considered**: Passing everything in request.state and having routes read it — would not use DI and would make tests harder; rejected.

---

## 6. Response models

**Decision**: Define Pydantic models for the success response (e.g. `ExtractResponse` with `text`, `id`, `format`) and use them as the route’s `response_model`. Use a single error response model if we standardize error body shape. Existing response shape is preserved.

**Rationale**: Ensures consistent schema (FR-007) and documents the API; no new dependency (Pydantic already in use).

**Alternatives considered**: Returning raw dicts — no validation; keeping current dict but adding a response_model — minimal change and satisfies the spec.
