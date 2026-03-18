from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.certifications_parser import parse_certifications_section
from src.domain.education_parser import parse_education_section
from src.domain.experience_parser import parse_experience_section
from src.domain.personal_info.entities.personal_info import PersonalInfo
from src.domain.section_detector import split_into_sections
from src.domain.skills_extractor import extract_skills


@dataclass
class CvParsedData:
    experience: list[dict]
    education: list[dict]
    skills: list[str]
    certifications: list[str]
    personal_info: dict[str, str | None] = field(default_factory=lambda: PersonalInfo().to_dict())


def parse_cv(raw_text: str) -> CvParsedData:
    sections = split_into_sections(raw_text)

    experience_section = sections.get("experience", "")
    education_section = sections.get("education", "")
    skills_section = sections.get("skills", "")
    certifications_section = sections.get("certifications", "")

    experience = parse_experience_section(experience_section)
    education = parse_education_section(education_section)

    skills_source = "\n".join(
        (
            part
            for part in [
                skills_section,
                experience_section,
                education_section,
                certifications_section,
            ]
            if part
        )
    )
    skills = extract_skills(skills_source)

    certifications = parse_certifications_section(certifications_section)

    from src.domain.personal_info.services.personal_info_extractor import (
        extract_personal_info,
    )

    personal_info = extract_personal_info(raw_text)

    return CvParsedData(
        experience=experience,
        education=education,
        skills=skills,
        certifications=certifications,
        personal_info=personal_info,
    )
