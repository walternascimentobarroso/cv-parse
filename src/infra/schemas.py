from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

# Shape of parsed_data stored/returned by the API
# (experience, education, skills, certifications).
ParsedDataDict = dict[str, object]


class ExtractionRecord(BaseModel):
    filename: str | None
    content_type: str
    size_bytes: int
    extracted_text: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    parsed_data: ParsedDataDict | None = None

    def to_mongo(self) -> dict[str, object]:
        return self.model_dump()


class HealthResponse(BaseModel):
    """GET /health response."""

    status: str


class ExtractResponse(BaseModel):
    """POST /extract success response."""

    text: str
    id: str
    format: str
    parsed_data: ParsedDataDict | None = None


class ExtractionDetailResponse(BaseModel):
    """Single extraction record for GET by id, list item, PATCH response."""

    id: str
    filename: str | None
    content_type: str
    size_bytes: int
    extracted_text: str
    status: str
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    parsed_data: ParsedDataDict | None = None


class ExtractionListResponse(BaseModel):
    """GET /extractions response: list of active extractions."""

    items: list[ExtractionDetailResponse]


class ExtractionUpdateRequest(BaseModel):
    """PATCH /extractions/{id} body: only allowed updatable fields."""

    extracted_text: str | None = None


class ExtractionUpdateResponse(BaseModel):
    """PATCH /extractions/{id} response: full record after update."""

    id: str
    filename: str | None
    content_type: str
    size_bytes: int
    extracted_text: str
    status: str
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    parsed_data: ParsedDataDict | None = None


class ErrorDetail(BaseModel):
    """Standard error body (e.g. 400, 413, 500)."""

    detail: str
