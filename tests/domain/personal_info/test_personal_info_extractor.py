from unittest.mock import MagicMock, patch

from src.domain.personal_info.services import personal_info_extractor as pie
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
        msg = f"Expected email, got {result!r}"
        raise AssertionError(msg)


def test_extract_email_invalid_returns_none() -> None:
    text = "Contact: ada.lovelace(at)example(dot)com"
    result = extract_email(text)
    if result is not None:
        msg = f"Expected None for invalid email, got {result!r}"
        raise AssertionError(msg)


def test_extract_email_empty_text_returns_none() -> None:
    if extract_email("") is not None:
        msg = "Expected None for empty text"
        raise AssertionError(msg)


def test_extract_links_linkedin_and_github() -> None:
    text = "Profiles: https://www.linkedin.com/in/ada and github.com/ada"
    result = extract_links(text)
    linkedin = result["linkedin"]
    github = result["github"]
    if not linkedin or "linkedin.com" not in linkedin:
        msg = f"Expected linkedin.com URL, got {linkedin!r}"
        raise AssertionError(msg)
    if not github or "github.com" not in github:
        msg = f"Expected github.com URL, got {github!r}"
        raise AssertionError(msg)


def test_extract_name_from_header_lines() -> None:
    lines = [
        "",
        "Ada Lovelace",
        "ada.lovelace@example.com",
        "https://www.linkedin.com/in/ada",
    ]
    result = extract_name(lines)
    if result != "Ada Lovelace":
        msg = f"Expected name 'Ada Lovelace', got {result!r}"
        raise AssertionError(msg)


def test_extract_summary_after_header_block() -> None:
    header = "\n".join(["Ada Lovelace", "ada@example.com"] + [""] * 8)
    body = "Software engineer with experience in distributed systems.\nMore text."
    text = f"{header}\n{body}"
    result = extract_summary(text)
    if "Software engineer" not in (result or ""):
        msg = f"Expected summary paragraph, got {result!r}"
        raise AssertionError(msg)


def test_extract_personal_info_end_to_end() -> None:
    text = """Ada Lovelace
ada.lovelace@example.com
https://www.linkedin.com/in/adalovelace
github.com/adalovelace

Software engineer with experience in distributed systems.
"""
    result = extract_personal_info(text)
    if result["full_name"] != "Ada Lovelace":
        msg = f"Expected full_name, got {result['full_name']!r}"
        raise AssertionError(msg)
    if result["email"] != "ada.lovelace@example.com":
        msg = f"Expected email, got {result['email']!r}"
        raise AssertionError(msg)
    if not result["linkedin"] or "linkedin.com" not in result["linkedin"]:
        msg = f"Expected linkedin, got {result['linkedin']!r}"
        raise AssertionError(msg)
    if not result["github"] or "github.com" not in result["github"]:
        msg = f"Expected github, got {result['github']!r}"
        raise AssertionError(msg)
    if not result["summary"]:
        msg = "Expected summary to be populated"
        raise AssertionError(msg)


def test_extract_phone_simple() -> None:
    text = "Phone: +1 (555) 123-4567"
    result = extract_phone(text)
    if "+1 (555) 123-4567" not in (result or ""):
        msg = f"Expected phone string preserved, got {result!r}"
        raise AssertionError(msg)


def test_extract_phone_too_short_returns_none() -> None:
    text = "Phone: 123-45"
    result = extract_phone(text)
    if result is not None:
        msg = f"Expected None for too-short phone, got {result!r}"
        raise AssertionError(msg)


def test_extract_phone_empty_text_returns_none() -> None:
    if extract_phone("") is not None:
        msg = "Expected None for empty text"
        raise AssertionError(msg)


def test_extract_phone_match_but_fewer_than_seven_digits_returns_none() -> None:
    # Matches PHONE_REGEX but digit count (excluding +) is 6.
    text = "Call +1 234 56"
    result = extract_phone(text)
    if result is not None:
        msg = f"Expected None when <7 digits, got {result!r}"
        raise AssertionError(msg)


def test_iter_urls_empty_text_returns_nothing() -> None:
    if list(pie._iter_urls("")) != []:
        msg = "Expected empty iterator for empty text"
        raise AssertionError(msg)


def test_iter_urls_skips_whitespace_only_match() -> None:
    mock_match = MagicMock()
    mock_match.group.return_value = "   "

    def _fake_finditer(_t: str):
        return iter([mock_match])

    with patch.object(pie, "_url_regex_finditer", side_effect=_fake_finditer):
        if list(pie._iter_urls("x")) != []:
            msg = "Expected no URLs when group strips to empty"
            raise AssertionError(msg)


def test_normalize_url_empty_netloc_returns_none() -> None:
    if pie._normalize_url("https://") is not None:
        msg = "Expected None for URL with empty netloc"
        raise AssertionError(msg)


def test_classify_url_linkedin_github_and_other() -> None:
    li, gh = pie._classify_url("https://www.linkedin.com/in/x")
    if li is None or "linkedin" not in li:
        msg = f"Expected linkedin URL, got {li!r}"
        raise AssertionError(msg)
    if gh is not None:
        msg = f"Expected github None, got {gh!r}"
        raise AssertionError(msg)

    li2, gh2 = pie._classify_url("https://github.com/u")
    if li2 is not None or gh2 is None or "github.com" not in gh2:
        msg = f"Expected github only, got {li2!r} {gh2!r}"
        raise AssertionError(msg)

    li3, gh3 = pie._classify_url("https://example.com/path")
    if li3 is not None or gh3 is not None:
        msg = f"Expected both None, got {li3!r} {gh3!r}"
        raise AssertionError(msg)


def test_normalize_url_empty_string_returns_none() -> None:
    if pie._normalize_url("") is not None:
        msg = "Expected None for empty string URL input"
        raise AssertionError(msg)


def test_normalize_url_http_upgraded_to_https() -> None:
    out = pie._normalize_url("http://example.com/path")
    if out != "https://example.com/path":
        msg = f"Expected https upgrade, got {out!r}"
        raise AssertionError(msg)


def test_choose_linkedin_skips_unnormalizable_then_picks() -> None:
    out = pie._choose_linkedin(["https://", "https://www.linkedin.com/in/ada"])
    if out is None or "linkedin.com" not in out:
        msg = f"Expected linkedin after skip, got {out!r}"
        raise AssertionError(msg)


def test_choose_github_skips_unnormalizable_then_picks() -> None:
    out = pie._choose_github(["https://", "github.com/ada"])
    if out is None or "github.com" not in out:
        msg = f"Expected github after skip, got {out!r}"
        raise AssertionError(msg)


def test_choose_github_no_github_url_returns_none() -> None:
    if pie._choose_github(["https://example.com"]) is not None:
        msg = "Expected None when no github URL"
        raise AssertionError(msg)


def test_extract_personal_website_skips_unnormalizable_and_known_hosts() -> None:
    urls = ["https://", "linkedin.com/in/ada", "github.com/ada", "ada.example.com"]
    email = "user@example.com"
    out = pie.extract_personal_website(urls, email)
    # Domain matches email domain, so it should be filtered out and return None.
    if out is not None:
        msg = f"Expected None personal website, got {out!r}"
        raise AssertionError(msg)


def test_extract_links_only_linkedin_github_none() -> None:
    result = extract_links("See https://www.linkedin.com/in/ada")
    if result["github"] is not None:
        msg = f"Expected github None, got {result['github']!r}"
        raise AssertionError(msg)


def test_extract_name_skips_email_http_https_lines() -> None:
    lines = ["x@y.com", "http://a.com", "https://b.com", "Real Name"]
    if extract_name(lines) != "Real Name":
        msg = "Expected name after skipping email/URLs"
        raise AssertionError(msg)


def test_extract_name_skips_experience_education_skills_heading_lines() -> None:
    if extract_name(["Experience at Acme", "Jane Doe"]) != "Jane Doe":
        msg = "Expected skip experience-like line"
        raise AssertionError(msg)
    if extract_name(["Education background", "Bob"]) != "Bob":
        msg = "Expected skip education-like line"
        raise AssertionError(msg)
    if extract_name(["Skills include Python", "Ann"]) != "Ann":
        msg = "Expected skip skills-like line"
        raise AssertionError(msg)


def test_extract_name_all_lines_skipped_returns_none() -> None:
    lines = ["", "a@b.c", "https://x.com", "Experience", "Education"]
    if extract_name(lines) is not None:
        msg = "Expected None when no usable name line"
        raise AssertionError(msg)


def test_extract_summary_empty_returns_none() -> None:
    if extract_summary("") is not None:
        msg = "Expected None for empty summary input"
        raise AssertionError(msg)


def test_extract_summary_single_paragraph_returns_none() -> None:
    if extract_summary("Only one block\nsecond line same paragraph") is not None:
        msg = "Expected None when fewer than two paragraphs"
        raise AssertionError(msg)


def test_extract_summary_second_paragraph_is_section_heading_returns_none() -> None:
    text = "Header line\n\nExperience\nEngineer at X"
    if extract_summary(text) is not None:
        msg = "Expected None when second paragraph starts as section heading"
        raise AssertionError(msg)


def test_extract_summary_second_paragraph_starts_education_skills_certifications() -> None:
    for heading, body in (
        ("Education", "MIT 2020"),
        ("Skills", "Python"),
        ("Certifications", "AWS"),
    ):
        text = f"Name\n\n{heading}\n{body}"
        if extract_summary(text) is not None:
            msg = f"Expected None for heading {heading!r}"
            raise AssertionError(msg)


def test_extract_summary_from_labeled_uses_blank_line_to_terminate() -> None:
    lines = [
        "Summary",
        "First line of summary",
        "",
        "Experience",
        "Engineer at X",
    ]
    text = "\n".join(lines)
    result = extract_summary(text)
    if result != "First line of summary":
        msg = f"Expected labeled summary until blank, got {result!r}"
        raise AssertionError(msg)


def test_extract_summary_from_labeled_no_content_returns_none() -> None:
    lines = [
        "Summary",
        "",
        "Experience",
        "Engineer at X",
    ]
    text = "\n".join(lines)
    result = extract_summary(text)
    if result is not None:
        msg = f"Expected None when no labeled summary body, got {result!r}"
        raise AssertionError(msg)


def test_extract_personal_info_missing_email_and_summary() -> None:
    text = """Ada Lovelace
github.com/adalovelace

Experience
Engineer at Acme
"""
    result = extract_personal_info(text)
    if result["email"] is not None:
        msg = f"Expected email None, got {result['email']!r}"
        raise AssertionError(msg)
    if result["summary"] is not None:
        msg = f"Expected summary None, got {result['summary']!r}"
        raise AssertionError(msg)


def test_extract_personal_info_empty_text_returns_all_keys() -> None:
    result = extract_personal_info("")
    expected_keys = {
        "full_name",
        "name",
        "email",
        "phone",
        "linkedin",
        "github",
        "website",
        "location",
        "summary",
    }
    if set(result.keys()) != expected_keys:
        msg = f"Expected keys {expected_keys}, got {set(result.keys())}"
        raise AssertionError(msg)
    if any(value is not None for value in result.values()):
        msg = f"Expected all None values, got {result!r}"
        raise AssertionError(msg)
