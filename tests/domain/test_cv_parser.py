"""Unit tests for CV parser (domain layer)."""

from src.domain.cv_parser import CvParsedData, parse_cv


def test_parse_cv_empty_text() -> None:
    result = parse_cv("")
    if not isinstance(result, CvParsedData):
        msg = f"Expected CvParsedData, got {type(result)}"
        raise AssertionError(msg)
    if result.experience != []:
        msg = f"Expected empty experience, got {result.experience!r}"
        raise AssertionError(msg)
    if result.education != []:
        msg = f"Expected empty education, got {result.education!r}"
        raise AssertionError(msg)
    if result.skills != []:
        msg = f"Expected empty skills, got {result.skills!r}"
        raise AssertionError(msg)
    if result.certifications != []:
        msg = f"Expected empty certifications, got {result.certifications!r}"
        raise AssertionError(msg)


def test_parse_cv_full_sections() -> None:
    text = """Experience
Engineer at Acme Ltd
2020 - 2022

Education
MIT, BSc 2016 - 2020

Skills
Python, AWS

Certifications
AWS Certified
"""
    result = parse_cv(text)
    if len(result.experience) != 1:
        msg = f"Expected 1 experience entry, got {len(result.experience)}"
        raise AssertionError(msg)
    if len(result.education) != 1:
        msg = f"Expected 1 education entry, got {len(result.education)}"
        raise AssertionError(msg)
    if "python" not in result.skills and "aws" not in result.skills:
        msg = f"Expected skills from text, got {result.skills!r}"
        raise AssertionError(msg)
    if "AWS Certified" not in result.certifications:
        msg = f"Expected certifications, got {result.certifications!r}"
        raise AssertionError(msg)


def test_parse_cv_skills_aggregated_from_all_sections() -> None:
    text = """Experience
Used Python and Docker at Acme.

Education
University of X.

Skills
AWS

Certifications
GCP
"""
    result = parse_cv(text)
    if "python" not in result.skills:
        msg = f"Expected python from experience, got {result.skills!r}"
        raise AssertionError(msg)
    if "docker" not in result.skills:
        msg = f"Expected docker from experience, got {result.skills!r}"
        raise AssertionError(msg)
    if "aws" not in result.skills:
        msg = f"Expected aws from skills section, got {result.skills!r}"
        raise AssertionError(msg)


def test_parse_cv_only_experience_section() -> None:
    text = "Experience\nDev at X\n2019 - 2020"
    result = parse_cv(text)
    if len(result.experience) != 1:
        msg = f"Expected 1 experience, got {len(result.experience)}"
        raise AssertionError(msg)
    if result.education != [] or result.certifications != []:
        msg = f"Expected empty education/certifications, got {result!r}"
        raise AssertionError(msg)


def test_parse_cv_only_education_section() -> None:
    text = "Education\nMIT, PhD 2015-2019"
    result = parse_cv(text)
    if len(result.education) != 1:
        msg = f"Expected 1 education, got {len(result.education)}"
        raise AssertionError(msg)
    if result.experience != []:
        msg = f"Expected empty experience, got {result.experience!r}"
        raise AssertionError(msg)


def test_cv_parsed_data_dataclass() -> None:
    data = CvParsedData(
        experience=[{"company": "X"}],
        education=[],
        skills=["python"],
        certifications=[],
    )
    if data.experience[0]["company"] != "X":
        msg = f"Expected company X, got {data.experience!r}"
        raise AssertionError(msg)
    if data.skills != ["python"]:
        msg = f"Expected skills ['python'], got {data.skills!r}"
        raise AssertionError(msg)
