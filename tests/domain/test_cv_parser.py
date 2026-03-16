"""Unit tests for CV parser (domain layer)."""

from src.domain.cv_parser import CvParsedData, parse_cv


def test_parse_cv_empty_text() -> None:
    result = parse_cv("")
    if not isinstance(result, CvParsedData):
        raise AssertionError(f"Expected CvParsedData, got {type(result)}")
    if result.experience != []:
        raise AssertionError(f"Expected empty experience, got {result.experience!r}")
    if result.education != []:
        raise AssertionError(f"Expected empty education, got {result.education!r}")
    if result.skills != []:
        raise AssertionError(f"Expected empty skills, got {result.skills!r}")
    if result.certifications != []:
        raise AssertionError(f"Expected empty certifications, got {result.certifications!r}")


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
        raise AssertionError(f"Expected 1 experience entry, got {len(result.experience)}")
    if len(result.education) != 1:
        raise AssertionError(f"Expected 1 education entry, got {len(result.education)}")
    if "python" not in result.skills and "aws" not in result.skills:
        raise AssertionError(f"Expected skills from text, got {result.skills!r}")
    if "AWS Certified" not in result.certifications:
        raise AssertionError(f"Expected certifications, got {result.certifications!r}")


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
        raise AssertionError(f"Expected python from experience, got {result.skills!r}")
    if "docker" not in result.skills:
        raise AssertionError(f"Expected docker from experience, got {result.skills!r}")
    if "aws" not in result.skills:
        raise AssertionError(f"Expected aws from skills section, got {result.skills!r}")


def test_parse_cv_only_experience_section() -> None:
    text = "Experience\nDev at X\n2019 - 2020"
    result = parse_cv(text)
    if len(result.experience) != 1:
        raise AssertionError(f"Expected 1 experience, got {len(result.experience)}")
    if result.education != [] or result.certifications != []:
        raise AssertionError(f"Expected empty education/certifications, got {result!r}")


def test_parse_cv_only_education_section() -> None:
    text = "Education\nMIT, PhD 2015-2019"
    result = parse_cv(text)
    if len(result.education) != 1:
        raise AssertionError(f"Expected 1 education, got {len(result.education)}")
    if result.experience != []:
        raise AssertionError(f"Expected empty experience, got {result.experience!r}")


def test_cv_parsed_data_dataclass() -> None:
    data = CvParsedData(
        experience=[{"company": "X"}],
        education=[],
        skills=["python"],
        certifications=[],
    )
    if data.experience[0]["company"] != "X":
        raise AssertionError(f"Expected company X, got {data.experience!r}")
    if data.skills != ["python"]:
        raise AssertionError(f"Expected skills ['python'], got {data.skills!r}")
