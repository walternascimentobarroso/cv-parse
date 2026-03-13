from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExtractionRecord(BaseModel):
    filename: str | None
    content_type: str
    size_bytes: int
    extracted_text: str
    status: str
    created_at: datetime

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


class ErrorDetail(BaseModel):
    """Standard error body (e.g. 400, 413, 500)."""

    detail: str

