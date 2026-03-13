"""
Shared test configuration and fixtures.

- TestClient uses a test app with a minimal lifespan (no real DB).
- get_repo and get_extractor are satisfied via app.state set in test lifespan.
- Use dependency_overrides to inject failing extractor for 500 tests.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes import router as api_router
from src.infra.extractors.registry import ExtractorRegistry


class InMemoryExtractionRepository:
    """In-memory double for ExtractionRepository; no real DB required."""

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


@asynccontextmanager
async def _test_lifespan(app: FastAPI):
    """Lifespan that sets app.state with in-memory repo and registry; no MongoDB."""
    app.state.extraction_repo = InMemoryExtractionRepository()
    app.state.document_extractor = ExtractorRegistry(
        mime_type_plain="text/plain",
        mime_type_pdf="application/pdf",
    )
    yield


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """FastAPI app with test lifespan (no real DB)."""
    app = FastAPI(title="Doc-to-Text API (test)", lifespan=_test_lifespan)
    app.include_router(api_router)
    return app


@pytest.fixture(scope="session")
def client(test_app: FastAPI) -> TestClient:
    """TestClient for API tests; uses test app so no real DB is required."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def extractor() -> ExtractorRegistry:
    """Shared extractor registry for domain-layer tests (no server)."""
    return ExtractorRegistry(
        mime_type_plain="text/plain",
        mime_type_pdf="application/pdf",
    )
