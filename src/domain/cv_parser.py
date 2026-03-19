from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.personal_info.entities.personal_info import PersonalInfo


@dataclass
class CvParsedData:
    experience: list[dict]
    education: list[dict]
    skills: list[str]
    certifications: list[str]
    personal_info: dict[str, str | None] = field(default_factory=lambda: PersonalInfo().to_dict())
    hard_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    languages: list[dict[str, str | None]] = field(default_factory=list)
    certification_details: list[dict[str, str | None]] = field(default_factory=list)


def parse_cv(raw_text: str) -> CvParsedData:
    from src.application.cv_parsing import build_parsed_cv

    return build_parsed_cv(raw_text)
