"""Unit tests for skills extractor (domain layer)."""

from src.domain.skills_extractor import DEFAULT_SKILLS, extract_skills


def test_extract_skills_empty_text_returns_empty() -> None:
    result = extract_skills("")
    if result != []:
        msg = f"Expected [], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_whitespace_only_returns_empty() -> None:
    result = extract_skills("   \n  ")
    if result != []:
        msg = f"Expected [], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_finds_from_default_catalog() -> None:
    text = "I use Python and Docker daily. Also AWS."
    result = extract_skills(text)
    if "python" not in result or "docker" not in result or "aws" not in result:
        msg = f"Expected python, docker, aws in result, got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_preserves_order_no_duplicates() -> None:
    text = "python python docker python"
    result = extract_skills(text)
    if result != ["python", "docker"]:
        msg = f"Expected ['python', 'docker'], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_uses_custom_catalog() -> None:
    text = "Expert in Rust and Go."
    result = extract_skills(text, skills_catalog=["rust", "go", "java"])
    if result != ["rust", "go"]:
        msg = f"Expected ['rust', 'go'], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_catalog_none_uses_default() -> None:
    text = "python"
    result = extract_skills(text, skills_catalog=None)
    if "python" not in result:
        msg = f"Expected python in result with default catalog, got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_skips_empty_tokens_in_catalog() -> None:
    text = "python"
    result = extract_skills(text, skills_catalog=["  ", "python", ""])
    if result != ["python"]:
        msg = f"Expected ['python'], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_case_insensitive_match() -> None:
    result = extract_skills("PYTHON and Docker", skills_catalog=["python", "docker"])
    if result != ["python", "docker"]:
        msg = f"Expected ['python', 'docker'], got {result!r}"
        raise AssertionError(msg)


def test_extract_skills_empty_catalog_returns_empty() -> None:
    result = extract_skills("anything", skills_catalog=[])
    if result != []:
        msg = f"Expected [], got {result!r}"
        raise AssertionError(msg)


def test_default_skills_constant_exists() -> None:
    if not DEFAULT_SKILLS or "python" not in DEFAULT_SKILLS:
        msg = "DEFAULT_SKILLS should contain python"
        raise AssertionError(msg)
