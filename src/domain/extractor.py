from __future__ import annotations

import io

import pdfplumber

from src.domain.constants import MIME_APPLICATION_PDF, MIME_TEXT_PLAIN


class SimpleDocumentExtractor:
    def __init__(self, allowed_content_types: list[str]) -> None:
        self._allowed = set(allowed_content_types)

    def extract(self, content: bytes, content_type: str) -> str:
        if content_type not in self._allowed:
            raise ValueError(f"Unsupported content type: {content_type}")

        if not content:
            return ""

        if content_type == MIME_TEXT_PLAIN:
            return content.decode("utf-8", errors="ignore")

        if content_type == MIME_APPLICATION_PDF:
            return self._extract_pdf(content)

        raise ValueError(f"Unsupported content type: {content_type}")

    def _extract_pdf(self, content: bytes) -> str:
        buffer = io.BytesIO(content)
        texts: list[str] = []
        with pdfplumber.open(buffer) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text)
        return "\n".join(texts).strip()

