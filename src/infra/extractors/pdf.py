"""PDF extractor strategy with error handling and logging."""

from __future__ import annotations

import io

import pdfplumber

from src.infra.logging_config import get_logger

logger = get_logger(__name__)


class PdfExtractor:
    """Extract text from PDF bytes using pdfplumber."""

    def extract(self, content: bytes) -> str:
        if not content:
            return ""
        buffer = io.BytesIO(content)
        texts: list[str] = []
        try:
            with pdfplumber.open(buffer) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    texts.append(page_text)
            return "\n".join(texts).strip()
        except Exception as exc:
            logger.exception("pdf_extraction_failure", extra={"error": str(exc)})
            raise ValueError(f"PDF extraction failed: {exc}") from exc
