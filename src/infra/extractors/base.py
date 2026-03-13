"""Strategy interface for document extraction (one strategy per content type)."""

from __future__ import annotations

from typing import Protocol


class DocumentExtractorStrategy(Protocol):
    """Extracts text from raw bytes for a single supported content type."""

    def extract(self, content: bytes) -> str:  # pragma: no cover
        ...
