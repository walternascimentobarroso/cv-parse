from __future__ import annotations

from typing import Protocol


class DocumentExtractor(Protocol):
    def extract(self, content: bytes, content_type: str) -> str:  # pragma: no cover
        ...

