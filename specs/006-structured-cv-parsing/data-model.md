## Data Model: Structured CV Parsing

### CV Document (MongoDB)

- **Collection**: existing CV collection (name reused from current implementation).  
- **Shape** (logical):

```json
{
  "_id": "ObjectId",
  "filename": "string",
  "content_type": "string",
  "size_bytes": 12345,
  "raw_text": "string",
  "parsed_data": {
    "experience": [],
    "education": [],
    "skills": [],
    "certifications": []
  },
  "status": "string",
  "created_at": "ISO-8601 datetime"
}
```

### Parsed Data

#### Experience Entry

- **company**: string (best-effort; may be empty if not detectable).  
- **role**: string (best-effort).  
- **start_date**: string (raw date text or normalized form, best-effort).  
- **end_date**: string (raw date text or normalized form, best-effort; may be `"Present"`).  
- **description**: string (concatenated description lines associated with this experience).

#### Education Entry

- **institution**: string (e.g. university, college, school).  
- **degree**: string (e.g. `BSc Computer Science`, `MBA`).  
- **start_year**: integer or null (best-effort).  
- **end_year**: integer or null (best-effort).

#### Skills

- **skills**: list of strings.  
  - Values are skill names matched against a predefined dictionary (e.g. `python`, `fastapi`, `mongodb`).  

#### Certifications

- **certifications**: list of strings.  
  - Values are certification names extracted from the certifications section (best-effort).

### Domain Types (Conceptual)

- **CvParsedData**  
  - `experience: list[ExperienceEntry]`  
  - `education: list[EducationEntry]`  
  - `skills: list[str]`  
  - `certifications: list[str]`

- **ExperienceEntry**  
  - `company: str | None`  
  - `role: str | None`  
  - `start_date: str | None`  
  - `end_date: str | None`  
  - `description: str | None`

- **EducationEntry**  
  - `institution: str | None`  
  - `degree: str | None`  
  - `start_year: int | None`  
  - `end_year: int | None`

