from __future__ import annotations

from src.infra.cv_extractors.languages_extractor import extract_languages


def test_extract_languages_skips_empty_and_bullet_only_lines() -> None:
    text = "- \n*   \n•   \n- English: Advanced"
    result = extract_languages(text)
    expected = [{"name": "English", "level": "Advanced"}]
    if result != expected:
        raise AssertionError(f"Expected {expected!r}, got {result!r}")


def test_extract_languages_simple_names_and_deduplicate() -> None:
    text = "English\nPortuguese\nenglish"
    result = extract_languages(text)
    names = [r["name"] for r in result]
    if "English" not in names:
        raise AssertionError(f"Expected 'English' in names, got {names!r}")
    if "Portuguese" not in names:
        raise AssertionError(f"Expected 'Portuguese' in names, got {names!r}")
    if len(names) != 2:
        raise AssertionError(f"Expected 2 names (deduped), got {len(names)}")


def test_extract_languages_early_empty_line_is_skipped() -> None:
    text = "\n\nEnglish"
    result = extract_languages(text)
    expected = [{"name": "English", "level": None}]
    if result != expected:
        raise AssertionError(f"Expected {expected!r}, got {result!r}")
