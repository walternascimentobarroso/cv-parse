# Data Model: Advanced CV Extraction (008)

## Document root (MongoDB / API)

Unchanged top-level extraction document. `parsed_data` is extended **additively**.

## `parsed_data` shape (logical)

### Legacy (must remain)

| Key | Type | Notes |
|-----|------|-------|
| `experience` | `object[]` | See Experience entry |
| `education` | `object[]` | See Education entry |
| `skills` | `string[]` | Flat list; should contain union of categorized skills when both exist |
| `certifications` | `string[]` | Certification names only |
| `personal_info` | `object` | See Personal info |

### Additive (008)

| Key | Type | Notes |
|-----|------|-------|
| `hard_skills` | `string[]` | From “Technical / Hard skills” sections |
| `soft_skills` | `string[]` | From “Soft skills” sections |
| `languages` | `{ name: string, level: string \| null }[]` | |
| `certification_details` | `{ name: string, issuer: string \| null }[]` | Parallel to `certifications` strings |

### Personal info (`parsed_data.personal_info`)

All keys from **007** preserved:

- `full_name`, `email`, `phone`, `linkedin`, `github`, `summary` (values `string | null` as today).

**Additive**:

- `name` — aligned with display name (may mirror `full_name` when single canonical name).
- `location` — city/region line when detected.
- `website` — personal site (not LinkedIn/GitHub).

### Experience entry

**Required legacy fields** (best-effort strings, may be empty/null per existing behavior):

- `company`, `role`, `start_date`, `end_date`, `description`

**Additive optional fields**:

- `location` — `string | null`
- `responsibilities` — `string[] | null` (e.g. from Task/Action)
- `technologies` — `string[] | null` (inline tech tokens or bullet detection)
- `achievements` — `string[] | null` (e.g. from Result)

### Education entry

**Legacy**: `institution`, `degree`, `start_year`, `end_year` (integers where applicable).

**Additive**: `field`, `start_date`, `end_date` (strings, best-effort).

## Validation rules

- No required non-null field except structural presence of keys where spec demands (e.g. `personal_info` keys exist).
- Email/URL validation remains as in 007 for stored personal_info fields.
- New lists default to `[]` when section absent; omit vs empty—prefer **empty array** for new additive list keys for simpler clients.

## Relationships

- `certifications[i]` should correspond semantically to `certification_details[i]` when both derived from same line (best-effort alignment).
- `skills` ⊇ `hard_skills ∪ soft_skills` when categorization succeeds.

## State

Stateless parsing: no transitions.
