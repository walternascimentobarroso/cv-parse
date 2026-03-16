## API Contract: CV Upload and Parsing

### Endpoint

- **Method**: POST  
- **Path**: `/api/cv/upload` (existing upload endpoint)  
- **Description**: Accepts a CV PDF, extracts raw text, parses it into structured data, and stores both in MongoDB.

### Request

- **Headers**:
  - `Content-Type: multipart/form-data`

- **Body**:
  - `file`: binary PDF file representing the CV.

### Successful Response (200 OK)

```json
{
  "id": "string",
  "filename": "cv.pdf",
  "content_type": "application/pdf",
  "size_bytes": 12345,
  "raw_text": "...",
  "parsed_data": {
    "experience": [
      {
        "company": "string",
        "role": "string",
        "start_date": "string",
        "end_date": "string",
        "description": "string"
      }
    ],
    "education": [
      {
        "institution": "string",
        "degree": "string",
        "start_year": 2015,
        "end_year": 2018
      }
    ],
    "skills": ["python", "fastapi"],
    "certifications": ["AWS Certified Solutions Architect"]
  },
  "status": "string",
  "created_at": "2026-03-16T12:00:00Z"
}
```

### Error Responses

- **400 Bad Request**  
  - Invalid or missing file in the request.

- **415 Unsupported Media Type**  
  - Uploaded file is not a supported CV document type.

- **500 Internal Server Error**  
  - Unexpected failure in text extraction, parsing, or storage; error is logged and a generic message is returned.

