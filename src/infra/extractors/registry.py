"""Registry: maps content_type to extractor strategy. Implements DocumentExtractor contract."""

from __future__ import annotations

from typing import Protocol

from src.infra.extractors.pdf import PdfExtractor
from src.infra.extractors.plain_text import PlainTextExtractor


class _ContentExtractor(Protocol):
    def extract(self, content: bytes) -> str: ...


class ExtractorRegistry:
    """Selects strategy by content type; implements DocumentExtractor for routes."""

    def __init__(self, mime_type_plain: str, mime_type_pdf: str) -> None:
        self._strategies: dict[str, _ContentExtractor] = {
            mime_type_plain: PlainTextExtractor(),
            mime_type_pdf: PdfExtractor(),
        }

    def extract(self, content: bytes, content_type: str) -> str:
        strategy = self._strategies.get(content_type)
        if strategy is None:
            raise ValueError(f"Unsupported content type: {content_type}")
        return strategy.extract(content)
