"""Document extractor: dispatches by content type. MIME types come from caller (e.g. config)."""

from __future__ import annotations

import io

import pdfplumber


class SimpleDocumentExtractor:
    def __init__(
        self,
        allowed_content_types: list[str],
        *,
        mime_type_plain: str = "text/plain",
        mime_type_pdf: str = "application/pdf",
    ) -> None:
        self._allowed = set(allowed_content_types)
        self._mime_plain = mime_type_plain
        self._mime_pdf = mime_type_pdf

    def extract(self, content: bytes, content_type: str) -> str:
        if content_type not in self._allowed:
            raise ValueError(f"Unsupported content type: {content_type}")

        if not content:
            return ""

        if content_type == self._mime_plain:
            return content.decode("utf-8", errors="ignore")

        if content_type == self._mime_pdf:
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

