"""FastAPI dependency providers: repo, extractor. Read from app.state set in lifespan."""

from __future__ import annotations

from fastapi import Request

from src.domain.document_extractor_contracts import DocumentExtractor
from src.infra.storage import ExtractionRepository


def get_repo(request: Request) -> ExtractionRepository:
    repo: ExtractionRepository = request.app.state.extraction_repo
    return repo


def get_extractor(request: Request) -> DocumentExtractor:
    extractor: DocumentExtractor = request.app.state.document_extractor
    return extractor
