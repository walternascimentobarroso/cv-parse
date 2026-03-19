# Research: Advanced CV Extraction (008)

## R1 — Where orchestration lives

**Decision**: Introduce a thin **application** module (e.g. `src/application/cv_parsing.py`) that calls domain-defined protocols and infra-backed extractors, replacing the monolithic `parse_cv` orchestration incrementally. Until migration completes, `parse_cv` may delegate to the same pipeline to avoid duplicate entrypoints.

**Rationale**: Satisfies FR-015 (domain abstractions, infra implementations) and keeps FastAPI routes depending on one stable function.

**Alternatives considered**: Keep all logic in `domain/cv_parser.py` (rejected: blurs domain vs infra). Full rewrite in one PR (rejected: violates incremental delivery).

---

## R2 — Additive JSON keys (certifications, skills)

**Decision**:

| Concept | Legacy key | Additive key |
|---------|------------|--------------|
| Certifications (strings) | `certifications: string[]` | unchanged |
| Certifications (structured) | — | `certification_details: { name, issuer? }[]` |
| Flat skills | `skills: string[]` | unchanged (union of hard + soft when categorized) |
| Categorized skills | — | `hard_skills: string[]`, `soft_skills: string[]` at `parsed_data` root |

**Rationale**: Matches spec FR-007/FR-008/FR-009; no type change on legacy fields.

**Alternatives considered**: Nested `skills: { hard, soft }` only (rejected: breaks list consumers).

---

## R3 — Feature flags

**Decision**: Optional settings flag `CV_PARSER_ENHANCED=true` (default **true** once shipped). When **false**, fall back to current `parse_experience_section` / single-path skills only for experience and categorization (personal_info and languages can still run if low-risk). Exact scope to be minimized in implementation—prefer one flag for “enhanced multi-block experience + STAR” only.

**Rationale**: Risk mitigation per user input; avoids permanent dual maintenance if default-on after validation.

**Alternatives considered**: No flag (rejected: harder rollback). Per-section flags (deferred: YAGNI until needed).

---

## R4 — STAR merge order

**Decision**: Deterministic order **Situation → Task → Action → Result** (labels matched case-insensitively, common abbreviations S/T/A/R). Whitespace-normalized; bullet lines concatenated with newlines. **Responsibilities** populated from Task + Action lines when each block is clearly delimited; **achievements** from Result when delimited.

**Rationale**: Meets FR-005 and SC-002 (no silent drops).

**Alternatives considered**: Alphabetical merge (rejected: nonsensical for STAR).

---

## R5 — Fixture strategy

**Decision**: Primary golden test: `tests/fixtures/profile.pdf` + `tests/fixtures/profile_expected.json`. If `profile.pdf` cannot be committed (privacy), use **synthetic text** fixtures mirroring the same expected JSON shape and add a separate optional integration test marked with `@pytest.mark.integration` for a local PDF path.

**Rationale**: Spec demands real CV; repo policy may require anonymization.

**Alternatives considered**: PDF-only tests (rejected: slow and brittle in CI without binary).

---

## R6 — Observability

**Decision**: Structured logs at **INFO** for pipeline stage boundaries (`cv_parse_stage`, stage name, duration ms). **DEBUG** logs for section boundaries and experience block count (no full PII in logs at INFO). Reuse `get_logger(__name__)` pattern.

**Rationale**: Constitution-friendly; avoids log noise and GDPR-adjacent concerns.

**Alternatives considered**: Print-based debug (rejected).

---

## R7 — Extractor registry (CV sections vs document MIME)

**Decision**: New **CV section extractor registry** in infra (e.g. `infra/cv_extractors/`), distinct from `ExtractorRegistry` (PDF/plain → text). Domain defines `Protocol` per section; infra registers implementations; application builds the composite parser.

**Rationale**: Avoids overloading the document MIME registry; clear naming.

**Alternatives considered**: Single mega-registry (rejected: confusion).
