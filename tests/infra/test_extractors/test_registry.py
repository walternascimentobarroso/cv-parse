"""Unit tests for extractor registry (strategy selection)."""

from __future__ import annotations

from src.domain.constants import MIME_APPLICATION_PDF, MIME_TEXT_PLAIN
from src.infra.extractors.registry import ExtractorRegistry


def test_registry_plain_text() -> None:
    registry = ExtractorRegistry()
    result = registry.extract(b"hello world", MIME_TEXT_PLAIN)
    if result != "hello world":
        raise AssertionError(f"Expected 'hello world', got {result!r}")


def test_registry_unsupported_type_raises() -> None:
    registry = ExtractorRegistry()
    try:
        registry.extract(b"x", "image/jpeg")
        raise AssertionError("Expected ValueError for unsupported type")
    except ValueError as e:
        if "Unsupported" not in str(e):
            raise AssertionError(f"Expected 'Unsupported' in error: {e}") from e


def test_registry_pdf_invalid_raises_value_error() -> None:
    """Registry delegates to PDF strategy; invalid PDF raises ValueError (logged by strategy)."""
    registry = ExtractorRegistry()
    try:
        registry.extract(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n", MIME_APPLICATION_PDF)
        raise AssertionError("Expected ValueError for invalid PDF")
    except ValueError as e:
        if "PDF extraction failed" not in str(e):
            raise AssertionError(f"Expected 'PDF extraction failed' in error: {e}") from e
