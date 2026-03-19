# Contract: CV section extractors (internal)

## Domain protocols (conceptual)

Each protocol: `extract(section_text: str, context: ParseContext) -> T` where `ParseContext` may include full raw text for cross-section hints (e.g. personal site only in header).

| Protocol | Output |
|----------|--------|
| `PersonalInfoExtractor` | Updates / merges `PersonalInfo` dict |
| `ExperienceExtractor` | `list[dict]` legacy-compatible experience entries |
| `SkillsExtractor` | `(skills: list[str], hard_skills: list[str], soft_skills: list[str])` |
| `LanguagesExtractor` | `list[{name, level}]` |
| `CertificationsExtractor` | `(certifications: list[str], details: list[{name, issuer}])` |

Education may remain domain parser initially or gain a parallel infra extractor in a later increment.

## Registration

- Infra module registers default implementations.
- Application wires: section split → per-section extractors → merge into `CvParsedData`.

## Testing contract

- Unit tests: pass **raw section strings** (and full CV text where needed) directly to extractors.
- Golden: `profile_expected.json` compared with tolerant subset assertions (required keys + counts) to reduce brittleness on whitespace.
