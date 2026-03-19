# Contract: `parsed_data` (008 extended)

Consumers MUST treat unknown keys as optional. Producers MUST NOT remove or rename keys documented in specs **006**, **007**, and this document.

## TypeScript-style sketch

```ts
type PersonalInfo = {
  full_name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  summary: string | null;
  // 008 additive
  name?: string | null;
  location?: string | null;
  website?: string | null;
};

type ExperienceEntry = {
  company: string;
  role: string;
  start_date: string | null;
  end_date: string | null;
  description: string;
  location?: string | null;
  responsibilities?: string[] | null;
  technologies?: string[] | null;
  achievements?: string[] | null;
};

type EducationEntry = {
  institution: string;
  degree: string;
  start_year?: number | null;
  end_year?: number | null;
  field?: string | null;
  start_date?: string | null;
  end_date?: string | null;
};

type LanguageEntry = {
  name: string;
  level: string | null;
};

type CertificationDetail = {
  name: string;
  issuer: string | null;
};

type ParsedData = {
  experience: ExperienceEntry[];
  education: EducationEntry[];
  skills: string[];
  certifications: string[];
  personal_info: PersonalInfo;
  hard_skills?: string[];
  soft_skills?: string[];
  languages?: LanguageEntry[];
  certification_details?: CertificationDetail[];
};
```

## API surface

- **POST `/extract`** response body: `parsed_data` optional on persisted record; shape as above when present.
- No new endpoints required for 008.

## Parser pipeline contract (internal)

- **Input**: UTF-8 `raw_text: str`.
- **Output**: `CvParsedData` dataclass serialized to dict (API/Mongo).
- **Determinism**: Same input → same output (fixed rules, no randomness, no network).
