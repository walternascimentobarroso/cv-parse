"""Plain text extractor strategy."""

from __future__ import annotations


class PlainTextExtractor:
    """Extract text from UTF-8 plain text bytes."""

    def extract(self, content: bytes) -> str:
        if not content:
            return ""
        return content.decode("utf-8", errors="ignore")
