"""Unit tests for section detector (domain layer)."""

from src.domain.section_detector import split_into_sections


def test_split_empty_text_returns_empty_sections() -> None:
    result = split_into_sections("")
    expected = {"experience": "", "education": "", "skills": "", "certifications": ""}
    if result != expected:
        raise AssertionError(f"Expected {expected!r}, got {result!r}")


def test_split_whitespace_only_returns_empty_sections() -> None:
    result = split_into_sections("   \n  \n  ")
    if result["experience"] != "" or result["education"] != "":
        raise AssertionError(f"Expected empty sections, got {result!r}")


def test_split_experience_heading_variants() -> None:
    for heading in ["Experience", "Work Experience", "Professional Experience", "Employment", "Career History"]:
        text = f"{heading}:\nSoftware Engineer at Acme"
        result = split_into_sections(text)
        if "Software Engineer at Acme" not in result["experience"]:
            raise AssertionError(f"For heading {heading!r}, expected content in experience, got {result!r}")


def test_split_education_heading_variants() -> None:
    for heading in ["Education", "Academic Background", "Academic History"]:
        text = f"{heading}\nMIT 2020"
        result = split_into_sections(text)
        if "MIT 2020" not in result["education"]:
            raise AssertionError(f"For heading {heading!r}, expected content in education, got {result!r}")


def test_split_skills_heading_variants() -> None:
    for heading in ["Skills", "Technical Skills", "Core Skills"]:
        text = f"{heading}\nPython, Java"
        result = split_into_sections(text)
        if "Python, Java" not in result["skills"]:
            raise AssertionError(f"For heading {heading!r}, expected content in skills, got {result!r}")


def test_split_certifications_heading_variants() -> None:
    for heading in ["Certifications", "Licenses", "Certificates"]:
        text = f"{heading}\nAWS Certified"
        result = split_into_sections(text)
        if "AWS Certified" not in result["certifications"]:
            raise AssertionError(f"For heading {heading!r}, expected content in certifications, got {result!r}")


def test_split_normalises_heading_strip_and_colon() -> None:
    text = "  Experience  :  \nJob at X"
    result = split_into_sections(text)
    if "Job at X" not in result["experience"]:
        raise AssertionError(f"Expected normalised heading to match, got {result!r}")


def test_split_unknown_heading_ignored_until_known() -> None:
    text = "Summary\nSome intro\nExperience\nEngineer at Y"
    result = split_into_sections(text)
    if "Engineer at Y" not in result["experience"]:
        raise AssertionError(f"Expected content after Experience only, got {result!r}")
    if "Some intro" in result["experience"]:
        raise AssertionError("Lines before first known heading should not appear in any section")


def test_split_empty_lines_preserved_in_section() -> None:
    text = "Experience\nLine one\n\nLine two"
    result = split_into_sections(text)
    if "Line one" not in result["experience"] or "Line two" not in result["experience"]:
        raise AssertionError(f"Expected both lines in experience, got {result!r}")


def test_split_multiple_sections() -> None:
    text = """Experience
Dev at Acme

Education
MIT 2015

Skills
Python

Certifications
AWS
"""
    result = split_into_sections(text)
    if "Dev at Acme" not in result["experience"]:
        raise AssertionError(f"Expected experience content, got {result['experience']!r}")
    if "MIT 2015" not in result["education"]:
        raise AssertionError(f"Expected education content, got {result['education']!r}")
    if "Python" not in result["skills"]:
        raise AssertionError(f"Expected skills content, got {result['skills']!r}")
    if "AWS" not in result["certifications"]:
        raise AssertionError(f"Expected certifications content, got {result['certifications']!r}")


def test_split_leading_empty_lines_then_heading() -> None:
    text = "\n\nExperience\nContent"
    result = split_into_sections(text)
    if result["experience"] != "Content":
        raise AssertionError(f"Expected 'Content' in experience, got {result['experience']!r}")
