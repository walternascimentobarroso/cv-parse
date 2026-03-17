from __future__ import annotations

from collections import defaultdict

SectionMap = dict[str, str]


_EXPERIENCE_HEADINGS = {
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "career history",
}

_EDUCATION_HEADINGS = {
    "education",
    "academic background",
    "academic history",
}

_SKILLS_HEADINGS = {
    "skills",
    "technical skills",
    "core skills",
}

_CERTIFICATIONS_HEADINGS = {
    "certifications",
    "licenses",
    "certificates",
    "licenses & certifications",
}

_LANGUAGES_HEADINGS = {
    "languages",
    "idiomas",
}


def _normalise_heading(raw: str) -> str:
    text = raw.strip().lower().rstrip(":")
    return " ".join(text.split())


def _classify_heading(normalised: str) -> str | None:
    if normalised in _EXPERIENCE_HEADINGS:
        return "experience"
    if normalised in _EDUCATION_HEADINGS:
        return "education"
    if normalised in _SKILLS_HEADINGS:
        return "skills"
    if normalised in _CERTIFICATIONS_HEADINGS:
        return "certifications"
    if normalised in _LANGUAGES_HEADINGS:
        return "languages"
    return None


def split_into_sections(raw_text: str) -> SectionMap:
    if not raw_text:
        return {
            "experience": "",
            "education": "",
            "skills": "",
            "certifications": "",
            "languages": "",
        }

    buckets: dict[str, list[str]] = defaultdict(list)
    current: str | None = None

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current is None:
                continue
            buckets[current].append("")
            continue

        heading = _normalise_heading(stripped)
        section = _classify_heading(heading)
        if section is not None:
            current = section
            continue

        if current is None:
            # No recognised heading yet; ignore for now to keep behaviour predictable.
            continue

        buckets[current].append(line.rstrip())

    return {
        "experience": "\n".join(buckets.get("experience", [])).strip(),
        "education": "\n".join(buckets.get("education", [])).strip(),
        "skills": "\n".join(buckets.get("skills", [])).strip(),
        "certifications": "\n".join(buckets.get("certifications", [])).strip(),
        "languages": "\n".join(buckets.get("languages", [])).strip(),
    }

