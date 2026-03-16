## Research Summary: Structured CV Parsing (without LLM)

### Decisions

- **Deterministic parsing only**  
  - Use line-by-line section detection, regex/pattern matching, and keyword dictionaries.  
  - Do not call any LLM, external AI, or heavy NLP models.

- **Section detection strategy**  
  - Maintain explicit, case-insensitive heading lists for: experience, education, skills, certifications.  
  - Treat a line as a heading when it contains only the heading text (ignoring punctuation) or when the heading appears at the start of the line followed by a separator (e.g. `:`).  
  - Assign all subsequent lines to the current section until the next heading is found.

- **Experience parsing heuristics**  
  - Detect company and role using patterns like `Role at Company`, `Company – Role`, or bullet lines where one token looks like a company (contains common company suffixes) and the other like a role (contains typical titles).  
  - Detect dates using simple regexes for ranges:  
    - `MMM YYYY - MMM YYYY`, `YYYY - YYYY`, `MMM YYYY – Present`, `YYYY – Present`.  
  - Treat adjacent lines following a header line as the description until the next header-like line or blank line.

- **Education parsing heuristics**  
  - Detect institution using capitalization and keywords (e.g. `University`, `College`, `Institute`, `School`).  
  - Detect degree using keywords (e.g. `BSc`, `MSc`, `Bachelor`, `Master`, `PhD`, `Diploma`) and capture them even when they appear on the same line as the institution.  
  - Extract year ranges (`YYYY - YYYY`) or single years and map them to `start_year` and `end_year` when possible.

- **Skills extraction strategy**  
  - Maintain a configurable list of known skills (e.g. programming languages, frameworks, tools).  
  - Perform case-insensitive, whole-word or token-based matching across either the skills section or the entire CV text.  
  - De-duplicate skills and preserve a stable output order (e.g. order of first appearance in text).

- **Certifications parsing**  
  - Within the certifications section, treat each non-empty line or bullet as a potential certification name.  
  - Optionally use simple patterns (e.g. contains `Certified`, `Certification`, acronym + vendor like `AWS`, `Azure`, `GCP`) to improve extraction, but accept raw names as-is.

- **MongoDB storage model**  
  - Extend the existing CV document to include a `parsed_data` field with four top-level keys: `experience`, `education`, `skills`, `certifications`.  
  - Keep `parsed_data` purely derived from `raw_text` to preserve determinism; it can be recomputed if rules change.

### Rationale

- Deterministic, rule-based parsers (as used in commercial CV parsing engines) successfully extract work history, education, skills, and certifications without AI by combining section detection with specialized heuristics per section.  
- A line-based, heading-driven approach matches how most CVs are formatted and is simple to debug and evolve as new real-world samples appear.  
- Keeping rules in small, focused modules allows us to refine specific behaviors (e.g. experience date formats) without risking regressions in other areas.

### Alternatives Considered

- **LLM-based or external AI parsing**  
  - Rejected because the feature explicitly forbids LLMs/external AI and must run deterministically and offline-compatible.

- **Heavy NLP pipelines (POS tagging, dependency parsing)**  
  - Rejected as unnecessary complexity for the current scope; simple regex and keyword-based heuristics are sufficient for the initial feature and align with YAGNI.

- **Single monolithic parser function**  
  - Rejected in favor of small, composable modules (section detector + per-section parsers) to respect Single-Responsibility and keep tests focused and fast.

