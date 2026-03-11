from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.routes import get_extractor, get_repo
from src.domain.extractor import SimpleDocumentExtractor
from src.main import app


class InMemoryExtractionRepository:
    def __init__(self) -> None:
        self.saved: list[dict[str, object]] = []

    async def save_extraction(
        self,
        *,
        filename: str | None,
        content_type: str,
        size_bytes: int,
        extracted_text: str,
        status: str = "success",
    ) -> str:
        record = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "extracted_text": extracted_text,
            "status": status,
        }
        self.saved.append(record)
        return str(len(self.saved))


@pytest.fixture(scope="session")
def client() -> TestClient:
    app.dependency_overrides[get_repo] = lambda: InMemoryExtractionRepository()
    app.dependency_overrides[get_extractor] = lambda: SimpleDocumentExtractor(
        ["text/plain", "application/pdf"]
    )

    with TestClient(app) as test_client:
        yield test_client

