"""
Shared test configuration and fixtures.

- TestClient uses a test app with a minimal lifespan (no real DB).
- get_repo and get_extractor are satisfied via app.state set in test lifespan.
- Use dependency_overrides to inject failing extractor for 500 tests.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes import router as api_router
from src.infra.extractors.registry import ExtractorRegistry


def _make_oid(i: int) -> str:
    """Format counter as 24-char hex for tests."""
    return f"{i:024x}"


class InMemoryExtractionRepository:
    """In-memory double for ExtractionRepository; no real DB required."""

    def __init__(self) -> None:
        self._counter = 0
        self._docs: dict[str, dict] = {}

    async def save_extraction(
        self,
        *,
        filename: str | None,
        content_type: str,
        size_bytes: int,
        extracted_text: str,
        status: str = "success",
        parsed_data: dict[str, object] | None = None,
    ) -> str:
        self._counter += 1
        oid = _make_oid(self._counter)
        now = datetime.now(UTC)
        record = {
            "_id": oid,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "extracted_text": extracted_text,
            "status": status,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
            "parsed_data": parsed_data,
        }
        self._docs[oid] = record
        return oid

    def _to_response(self, doc: dict) -> dict:
        out = dict(doc)
        out["id"] = out.pop("_id", "")
        return out

    async def find_by_id(self, extraction_id: str) -> dict | None:
        doc = self._docs.get(extraction_id)
        if doc is None or doc.get("deleted_at") is not None:
            return None
        return self._to_response(doc)

    async def find_all(self) -> list[dict]:
        return [self._to_response(d) for d in self._docs.values() if d.get("deleted_at") is None]

    async def update(self, extraction_id: str, payload: dict) -> dict | None:
        doc = self._docs.get(extraction_id)
        if doc is None or doc.get("deleted_at") is not None:
            return None
        for key, value in payload.items():
            doc[key] = value
        doc["updated_at"] = datetime.now(UTC)
        return self._to_response(doc)

    async def soft_delete(self, extraction_id: str) -> bool:
        doc = self._docs.get(extraction_id)
        if doc is None or doc.get("deleted_at") is not None:
            return False
        now = datetime.now(UTC)
        doc["deleted_at"] = now
        doc["updated_at"] = now
        return True

    async def restore(self, extraction_id: str) -> str:
        doc = self._docs.get(extraction_id)
        if doc is None:
            return "not_found"
        if doc.get("deleted_at") is None:
            return "not_deleted"
        now = datetime.now(UTC)
        doc["deleted_at"] = None
        doc["updated_at"] = now
        return "restored"

    async def force_delete(self, extraction_id: str) -> bool:
        if extraction_id not in self._docs:
            return False
        del self._docs[extraction_id]
        return True


@asynccontextmanager
async def _test_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan that sets app.state with in-memory repo and registry; no MongoDB."""
    await asyncio.sleep(0)  # Yield control so this context manager is genuinely async
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
def client(test_app: FastAPI) -> Iterator[TestClient]:
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
