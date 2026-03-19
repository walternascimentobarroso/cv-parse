"""Unit tests for extractor registry and extractor strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Never, Self

from src.infra.extractors.pdf import PdfExtractor
from src.infra.extractors.plain_text import PlainTextExtractor
from src.infra.extractors.registry import ExtractorRegistry

if TYPE_CHECKING:
    import pytest

    from src.infra.extractors.base import DocumentExtractorStrategy


def test_registry_plain_text() -> None:
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    result = registry.extract(b"hello world", "text/plain")
    if result != "hello world":
        msg = f"Expected 'hello world', got {result!r}"
        raise AssertionError(msg)


def test_registry_unsupported_type_raises() -> None:
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    try:
        registry.extract(b"x", "image/jpeg")
        msg = "Expected ValueError for unsupported type"
        raise AssertionError(msg)
    except ValueError as e:
        if "Unsupported" not in str(e):
            msg = f"Expected 'Unsupported' in error: {e}"
            raise AssertionError(msg) from e


def test_registry_pdf_invalid_raises_value_error() -> None:
    """Registry delegates to PDF strategy; invalid PDF raises ValueError (logged by strategy)."""
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    try:
        registry.extract(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n", "application/pdf")
        msg = "Expected ValueError for invalid PDF"
        raise AssertionError(msg)
    except ValueError as exc:
        if "PDF extraction failed" not in str(exc):
            msg = f"Expected 'PDF extraction failed' in error: {exc}"
            raise AssertionError(msg) from exc


def test_plain_text_extractor_empty_and_non_empty() -> None:
    extractor: DocumentExtractorStrategy = PlainTextExtractor()
    empty_result = extractor.extract(b"")
    if empty_result != "":
        msg = f"Expected empty string for empty content, got {empty_result!r}"
        raise AssertionError(msg)
    result = extractor.extract(b"hello")
    if result != "hello":
        msg = f"Expected 'hello', got {result!r}"
        raise AssertionError(msg)


def test_pdf_extractor_happy_path_and_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = PdfExtractor()

    class FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class FakePdf:
        def __init__(self) -> None:
            self.pages = [FakePage("p1"), FakePage("p2")]

        def __enter__(self) -> Self:
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

    import src.infra.extractors.pdf as pdf_module

    monkeypatch.setattr(pdf_module.pdfplumber, "open", lambda _: FakePdf())

    empty_result = extractor.extract(b"")
    if empty_result != "":
        msg = f"Expected empty string for empty content, got {empty_result!r}"
        raise AssertionError(msg)

    result = extractor.extract(b"%PDF-1.4")
    if result != "p1\np2":
        msg = f"Expected joined page text, got {result!r}"
        raise AssertionError(msg)


def test_pdf_extractor_logs_and_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = PdfExtractor()

    import src.infra.extractors.pdf as pdf_module

    def boom(_buffer) -> Never:
        msg = "pdf boom"
        raise RuntimeError(msg)

    monkeypatch.setattr(pdf_module.pdfplumber, "open", boom)

    try:
        extractor.extract(b"%PDF-1.4")
        msg = "Expected ValueError from PdfExtractor on failure"
        raise AssertionError(msg)
    except ValueError as exc:
        if "PDF extraction failed" not in str(exc):
            msg = f"Unexpected error message: {exc!r}"
            raise AssertionError(msg) from exc
