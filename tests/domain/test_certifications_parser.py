"""Unit tests for certifications parser (domain layer)."""

from src.domain.certifications_parser import parse_certifications_section


def test_parse_empty_returns_empty_list() -> None:
    result = parse_certifications_section("")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_whitespace_only_returns_empty_list() -> None:
    result = parse_certifications_section("   \n  ")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_single_line_no_bullet() -> None:
    result = parse_certifications_section("AWS Certified Solutions Architect")
    if result != ["AWS Certified Solutions Architect"]:
        raise AssertionError(f"Expected single item, got {result!r}")


def test_parse_line_with_dash_bullet() -> None:
    result = parse_certifications_section("- AWS Certified")
    if result != ["AWS Certified"]:
        raise AssertionError(f"Expected bullet stripped, got {result!r}")


def test_parse_line_with_asterisk_bullet() -> None:
    result = parse_certifications_section("* Python Professional")
    if result != ["Python Professional"]:
        raise AssertionError(f"Expected bullet stripped, got {result!r}")


def test_parse_line_with_bullet_char() -> None:
    result = parse_certifications_section("• Kubernetes Admin")
    if result != ["Kubernetes Admin"]:
        raise AssertionError(f"Expected bullet stripped, got {result!r}")


def test_parse_line_multiple_bullets_stripped() -> None:
    result = parse_certifications_section("--- Deep cert")
    if result != ["Deep cert"]:
        raise AssertionError(f"Expected all bullets stripped, got {result!r}")


def test_parse_empty_line_skipped() -> None:
    result = parse_certifications_section("First\n\nSecond")
    if result != ["First", "Second"]:
        raise AssertionError(f"Expected two items, got {result!r}")


def test_parse_line_only_bullets_becomes_empty_skipped() -> None:
    result = parse_certifications_section("- * •")
    if result != []:
        raise AssertionError(f"Expected [] (line becomes empty), got {result!r}")


def test_parse_multiple_certifications() -> None:
    text = "- AWS\n* GCP\n  Oracle DB"
    result = parse_certifications_section(text)
    if result != ["AWS", "GCP", "Oracle DB"]:
        raise AssertionError(f"Expected three items, got {result!r}")
