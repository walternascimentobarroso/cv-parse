"""Orchestrates CV text → structured parsed_data (application layer)."""

from __future__ import annotations

import os
import time

from src.domain.certifications_parser import parse_certifications_section
from src.domain.cv_parser import CvParsedData
from src.domain.education_parser import parse_education_section
from src.domain.experience_parser import parse_experience_section
from src.domain.personal_info.entities.personal_info import PersonalInfo
from src.domain.personal_info.services.personal_info_extractor import (
    extract_personal_info,
)
from src.domain.section_detector import split_into_sections
from src.domain.skills_extractor import extract_skills
from src.infra.cv_extractors.certification_structured import (
    certification_details_from_strings,
)
from src.infra.cv_extractors.experience_extractor import parse_experience_multi
from src.infra.cv_extractors.languages_extractor import extract_languages
from src.infra.cv_extractors.skills_categorized import extract_hard_and_soft_skills
from src.infra.logging_config import get_logger

logger = get_logger(__name__)


def _enhanced_experience_enabled() -> bool:
    v = (os.environ.get("CV_PARSER_ENHANCED") or "true").strip().lower()
    return v not in ("0", "false", "no", "off")


def _merge_flat_skills(
    catalog_skills: list[str],
    hard: list[str],
    soft: list[str],
) -> list[str]:
    seen: set[str] = {x.lower() for x in catalog_skills}
    out = list(catalog_skills)
    for s in hard + soft:
        token = s.strip()
        if not token:
            continue
        key = token.lower()
        if key not in seen:
            seen.add(key)
            out.append(token)
    return out


def _log_stage(stage: str, start: float) -> None:
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info("cv_parse_stage %s elapsed_ms=%s", stage, elapsed_ms)


def build_parsed_cv(raw_text: str) -> CvParsedData:
    if not raw_text.strip():
        return empty_parsed_cv()

    t = time.perf_counter()
    sections = split_into_sections(raw_text)
    _log_stage("split_sections", t)

    t = time.perf_counter()
    experience_section = sections.get("experience", "")
    if _enhanced_experience_enabled():
        experience = [dict(e) for e in parse_experience_multi(experience_section)]
    else:
        experience = parse_experience_section(experience_section)
    _log_stage("experience", t)

    t = time.perf_counter()
    education = parse_education_section(sections.get("education", ""))
    _log_stage("education", t)

    t = time.perf_counter()
    skills_section = sections.get("skills", "")
    hard_skills, soft_skills = extract_hard_and_soft_skills(skills_section)
    skills_source = "\n".join(
        part
        for part in [
            skills_section,
            experience_section,
            sections.get("education", ""),
            sections.get("certifications", ""),
        ]
        if part
    )
    catalog_skills = extract_skills(skills_source)
    skills = _merge_flat_skills(catalog_skills, hard_skills, soft_skills)
    _log_stage("skills", t)

    t = time.perf_counter()
    certifications_section = sections.get("certifications", "")
    certifications = parse_certifications_section(certifications_section)
    certification_details = certification_details_from_strings(certifications)
    _log_stage("certifications", t)

    t = time.perf_counter()
    personal_info = extract_personal_info(raw_text)
    _log_stage("personal_info", t)

    t = time.perf_counter()
    languages = extract_languages(sections.get("languages", ""))
    _log_stage("languages", t)

    return CvParsedData(
        experience=experience,
        education=education,
        skills=skills,
        certifications=certifications,
        personal_info=personal_info,
        hard_skills=hard_skills,
        soft_skills=soft_skills,
        languages=languages,
        certification_details=certification_details,
    )


def empty_parsed_cv() -> CvParsedData:
    return CvParsedData(
        experience=[],
        education=[],
        skills=[],
        certifications=[],
        personal_info=PersonalInfo().to_dict(),
    )
