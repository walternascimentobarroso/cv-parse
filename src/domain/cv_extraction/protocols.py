"""Domain-level typing for CV section extractors (implemented in infra)."""

from __future__ import annotations

from typing import Any, Protocol


class ExperienceSectionParser(Protocol):
    def parse(self, experience_section_text: str) -> list[dict[str, Any]]: ...


class SkillsCategorizer(Protocol):
    def categorize(self, skills_section_text: str) -> tuple[list[str], list[str]]: ...


class LanguagesParser(Protocol):
    def parse(self, languages_section_text: str) -> list[dict[str, str | None]]: ...
