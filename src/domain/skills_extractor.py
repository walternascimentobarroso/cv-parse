from __future__ import annotations

from collections import OrderedDict


DEFAULT_SKILLS: list[str] = [
    "python",
    "php",
    "aws",
    "docker",
    "kubernetes",
    "mongodb",
    "mysql",
    "fastapi",
    "django",
    "react",
    "terraform",
]


def extract_skills(text: str, *, skills_catalog: list[str] | None = None) -> list[str]:
    if not text:
        return []

    catalog = skills_catalog or DEFAULT_SKILLS
    lowered_text = text.lower()

    found: "OrderedDict[str, None]" = OrderedDict()
    for skill in catalog:
        token = skill.strip()
        if not token:
            continue
        needle = token.lower()
        if needle in lowered_text and token not in found:
            found[token] = None

    return list(found.keys())

