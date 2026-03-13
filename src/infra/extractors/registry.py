"""Registry: maps content_type to extractor strategy. Implements DocumentExtractor contract."""

from __future__ import annotations

from src.domain.constants import MIME_APPLICATION_PDF, MIME_TEXT_PLAIN
from src.domain.document_extractor_contracts import DocumentExtractor
from src.infra.extractors.pdf import PdfExtractor
from src.infra.extractors.plain_text import PlainTextExtractor


class ExtractorRegistry:
    """Selects strategy by content type; implements DocumentExtractor for routes."""

    def __init__(self) -> None:
        self._strategies: dict[str, object] = {
            MIME_TEXT_PLAIN: PlainTextExtractor(),
            MIME_APPLICATION_PDF: PdfExtractor(),
        }

    def extract(self, content: bytes, content_type: str) -> str:
        strategy = self._strategies.get(content_type)
        if strategy is None:
            raise ValueError(f"Unsupported content type: {content_type}")
        return strategy.extract(content)
