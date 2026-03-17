"""Extractor strategies and registry (strategy pattern)."""

from src.infra.extractors.pdf import PdfExtractor
from src.infra.extractors.plain_text import PlainTextExtractor
from src.infra.extractors.registry import ExtractorRegistry

__all__ = ["PdfExtractor", "PlainTextExtractor", "ExtractorRegistry"]
