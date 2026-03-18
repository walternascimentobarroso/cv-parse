from src.domain.personal_info.services.personal_info_extractor import (
    extract_email,
    extract_links,
    extract_name,
    extract_personal_info,
    extract_phone,
    extract_summary,
)


def test_extract_email_simple() -> None:
    text = "Contact: ada.lovelace@example.com"
    result = extract_email(text)
    if result != "ada.lovelace@example.com":
        raise AssertionError(f"Expected email, got {result!r}")


def test_extract_email_invalid_returns_none() -> None:
    text = "Contact: ada.lovelace(at)example(dot)com"
    result = extract_email(text)
    if result is not None:
        raise AssertionError(f"Expected None for invalid email, got {result!r}")


def test_extract_links_linkedin_and_github() -> None:
    text = "Profiles: https://www.linkedin.com/in/ada and github.com/ada"
    result = extract_links(text)
    linkedin = result["linkedin"]
    github = result["github"]
    if not linkedin or "linkedin.com" not in linkedin:
        raise AssertionError(f"Expected linkedin.com URL, got {linkedin!r}")
    if not github or "github.com" not in github:
        raise AssertionError(f"Expected github.com URL, got {github!r}")


def test_extract_name_from_header_lines() -> None:
    lines = [
        "",
        "Ada Lovelace",
        "ada.lovelace@example.com",
        "https://www.linkedin.com/in/ada",
    ]
    result = extract_name(lines)
    if result != "Ada Lovelace":
        raise AssertionError(f"Expected name 'Ada Lovelace', got {result!r}")


def test_extract_summary_after_header_block() -> None:
    header = "\n".join(["Ada Lovelace", "ada@example.com"] + [""] * 8)
    body = "Software engineer with experience in distributed systems.\nMore text."
    text = f"{header}\n{body}"
    result = extract_summary(text)
    if "Software engineer" not in (result or ""):
        raise AssertionError(f"Expected summary paragraph, got {result!r}")


def test_extract_personal_info_end_to_end() -> None:
    text = """Ada Lovelace
ada.lovelace@example.com
https://www.linkedin.com/in/adalovelace
github.com/adalovelace

Software engineer with experience in distributed systems.
"""
    result = extract_personal_info(text)
    if result["full_name"] != "Ada Lovelace":
        raise AssertionError(f"Expected full_name, got {result['full_name']!r}")
    if result["email"] != "ada.lovelace@example.com":
        raise AssertionError(f"Expected email, got {result['email']!r}")
    if not result["linkedin"] or "linkedin.com" not in result["linkedin"]:
        raise AssertionError(f"Expected linkedin, got {result['linkedin']!r}")
    if not result["github"] or "github.com" not in result["github"]:
        raise AssertionError(f"Expected github, got {result['github']!r}")
    if not result["summary"]:
        raise AssertionError("Expected summary to be populated")


def test_extract_phone_simple() -> None:
    text = "Phone: +1 (555) 123-4567"
    result = extract_phone(text)
    if "+1 (555) 123-4567" not in (result or ""):
        raise AssertionError(f"Expected phone string preserved, got {result!r}")


def test_extract_phone_too_short_returns_none() -> None:
    text = "Phone: 123-45"
    result = extract_phone(text)
    if result is not None:
        raise AssertionError(f"Expected None for too-short phone, got {result!r}")


def test_extract_personal_info_missing_email_and_summary() -> None:
    text = """Ada Lovelace
github.com/adalovelace

Experience
Engineer at Acme
"""
    result = extract_personal_info(text)
    if result["email"] is not None:
        raise AssertionError(f"Expected email None, got {result['email']!r}")
    if result["summary"] is not None:
        raise AssertionError(f"Expected summary None, got {result['summary']!r}")


def test_extract_personal_info_empty_text_returns_all_keys() -> None:
    result = extract_personal_info("")
    expected_keys = {
        "full_name",
        "email",
        "phone",
        "linkedin",
        "github",
        "summary",
    }
    if set(result.keys()) != expected_keys:
        raise AssertionError(f"Expected keys {expected_keys}, got {set(result.keys())}")
    if any(value is not None for value in result.values()):
        raise AssertionError(f"Expected all None values, got {result!r}")

