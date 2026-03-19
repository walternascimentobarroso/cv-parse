"""Golden-style test: profile.pdf → parse_cv matches expected criteria."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast

import pytest

from src.domain.cv_parser import CvParsedData, parse_cv
from src.infra.extractors.pdf import PdfExtractor


class ProfileExpectations(TypedDict):
    min_experience_entries: int
    email: str
    linkedin_host: str
    website_host: str
    location_substring: str
    summary_substring: str
    min_hard_skills: int
    min_soft_skills: int
    min_languages: int
    certification_substring: str
    experience_company_substrings: list[str]


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PROFILE_PDF = FIXTURES / "profile.pdf"
EXPECTED_JSON = FIXTURES / "profile_expected.json"


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _assert_personal(pi: dict[str, str | None], exp: ProfileExpectations) -> None:
    _require(pi.get("email") == exp["email"], "email")
    _require(exp["linkedin_host"] in (pi.get("linkedin") or ""), "linkedin")
    _require(exp["website_host"] in (pi.get("website") or ""), "website")
    _require(exp["location_substring"] in (pi.get("location") or ""), "location")
    summary = pi.get("summary") or ""
    _require(exp["summary_substring"].lower() in summary.lower(), "summary")


def _assert_experience(entries: list[dict[str, object]], exp: ProfileExpectations) -> None:
    _require(len(entries) >= exp["min_experience_entries"], "experience count")
    joined = str(entries).lower()
    for frag in exp["experience_company_substrings"]:
        _require(frag.lower() in joined, f"company {frag!r}")


def _assert_skills_langs_certs(data: CvParsedData, exp: ProfileExpectations) -> None:
    _require(len(data.hard_skills) >= exp["min_hard_skills"], "hard_skills")
    _require(len(data.soft_skills) >= exp["min_soft_skills"], "soft_skills")
    _require(len(data.languages) >= exp["min_languages"], "languages")
    cert_blob = " ".join(data.certifications).lower()
    _require(exp["certification_substring"].lower() in cert_blob, "certs")


@pytest.mark.skipif(not PROFILE_PDF.is_file(), reason="tests/fixtures/profile.pdf missing")
def test_profile_pdf_matches_expected_criteria() -> None:
    raw = PdfExtractor().extract(PROFILE_PDF.read_bytes())
    data = parse_cv(raw)
    loaded = json.loads(EXPECTED_JSON.read_text())
    exp = cast("ProfileExpectations", loaded)
    _assert_experience(data.experience, exp)
    _assert_personal(data.personal_info, exp)
    _assert_skills_langs_certs(data, exp)
