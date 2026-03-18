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
    """Each line with a bullet starts a new certification."""
    text = "- AWS\n* GCP\n* Oracle DB"
    result = parse_certifications_section(text)
    if result != ["AWS", "GCP", "Oracle DB"]:
        raise AssertionError(f"Expected three items, got {result!r}")


def test_parse_continuation_line_merged_into_previous() -> None:
    """Lines without a bullet are merged into the previous certification (e.g. PDF wrap)."""
    text = "● PCAP – Certified Python Programmer 2024 Python\nInstitute"
    result = parse_certifications_section(text)
    if len(result) != 1:
        raise AssertionError(
            f"Expected 1 item (continuation merged), got {len(result)}: {result!r}",
        )
    if "Institute" not in result[0]:
        raise AssertionError(f"Expected 'Institute' merged into cert, got {result[0]!r}")


def test_parse_unicode_bullet_stripped() -> None:
    """Unicode bullet ● (U+25CF) is stripped like • (U+2022)."""
    result = parse_certifications_section("● AWS Certified")
    if result != ["AWS Certified"]:
        raise AssertionError(f"Expected bullet stripped, got {result!r}")
