from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urlparse

from src.domain.personal_info.entities.personal_info import PersonalInfo

HEADER_MAX_LINES = 10

EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
)

URL_REGEX = re.compile(
    # Match both full URLs (with scheme) and bare domains/paths like "github.com/ada".
    # We rely on `_normalize_url()` to prepend https:// when the scheme is missing.
    r"((?:https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?)",
    flags=re.IGNORECASE,
)

PHONE_REGEX = re.compile(
    r"(\+?\d[\d\s().-]{6,}\d)",
)


def extract_email(text: str) -> str | None:
    if not text:
        return None
    match = EMAIL_REGEX.search(text)
    if match is None:
        return None
    email = match.group(0).strip().lower()
    return email or None


def extract_phone(text: str) -> str | None:
    if not text:
        return None
    match = PHONE_REGEX.search(text)
    if match is None:
        return None
    raw = match.group(1)
    digits = "".join(ch for ch in raw if ch.isdigit() or ch == "+")
    if len(digits.replace("+", "")) < 7:
        return None
    return raw.strip()


def _url_regex_finditer(text: str) -> Iterable[re.Match[str]]:
    """Thin wrapper so tests can cover the empty-stripped match branch."""
    return URL_REGEX.finditer(text)


def _iter_urls(text: str) -> Iterable[str]:
    if not text:
        return []
    for match in _url_regex_finditer(text):
        url = match.group(1).strip()
        if not url:
            continue
        end = match.end()
        if end < len(text) and text[end] == "@":
            continue
        yield url


def _normalize_url(url: str) -> str | None:
    """
    Normalize URL for storage/display. Missing scheme defaults to https.
    Non-https schemes are upgraded to https (LinkedIn/GitHub support it; avoids clear-text URLs).
    """
    candidate = url.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    parsed = urlparse(candidate)
    if not parsed.netloc:
        return None
    scheme = (parsed.scheme or "https").lower()
    if scheme != "https":
        scheme = "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or ""
    return f"{scheme}://{netloc}{path}"


def _classify_url(normalized: str) -> tuple[str | None, str | None]:
    host = urlparse(normalized).netloc
    if "linkedin.com" in host:
        return normalized, None
    if host.endswith("github.com"):
        return None, normalized
    return None, None


def _choose_linkedin(urls: Iterable[str]) -> str | None:
    for url in urls:
        normalized = _normalize_url(url)
        if normalized is None:
            continue
        host = urlparse(normalized).netloc
        if "linkedin.com" in host:
            return normalized
    return None


def _choose_github(urls: Iterable[str]) -> str | None:
    for url in urls:
        normalized = _normalize_url(url)
        if normalized is None:
            continue
        host = urlparse(normalized).netloc
        if host.endswith("github.com"):
            return normalized
    return None


def extract_links(text: str) -> dict[str, str | None]:
    urls = list(_iter_urls(text))
    linkedin = _choose_linkedin(urls)
    github = _choose_github(urls)
    return {"linkedin": linkedin, "github": github}


def extract_personal_website(urls: Iterable[str], email: str | None) -> str | None:
    mail_domain: str | None = None
    if email and "@" in email:
        mail_domain = email.rsplit("@", 1)[-1].lower().strip()
    for url in urls:
        normalized = _normalize_url(url)
        if normalized is None:
            continue
        host = urlparse(normalized).netloc.lower()
        if "linkedin.com" in host or host.endswith("github.com"):
            continue
        if mail_domain and (host == mail_domain or host.endswith(f".{mail_domain}")):
            continue
        return normalized
    return None


def extract_location_from_header(header_lines: list[str]) -> str | None:
    """City/region line: comma-separated place, not email/URL/phone."""
    for raw in header_lines[1:12]:
        candidate = raw.strip()
        if not candidate:
            continue
        lowered = candidate.lower()
        if "@" in candidate or "http" in lowered or lowered.startswith("www."):
            continue
        if PHONE_REGEX.search(candidate) and len(candidate) < 30:
            continue
        if "," in candidate and 4 < len(candidate) < 120:
            return candidate
    return None


def _looks_like_heading(text: str) -> bool:
    lowered = text.lower()
    if "experience" in lowered:
        return True
    if "education" in lowered:
        return True
    if "skills" in lowered:
        return True
    return False


def _starts_with_section_heading(text: str) -> bool:
    """
    Summary text may contain words like "experience" mid-sentence; treat as a section
    heading only when the paragraph starts with one of the known section labels.
    """
    lowered = text.strip().lower()
    return (
        lowered.startswith("experience")
        or lowered.startswith("education")
        or lowered.startswith("skills")
        or lowered.startswith("certifications")
    )


def extract_name(lines: list[str]) -> str | None:
    for raw in lines:
        candidate = raw.strip()
        if not candidate:
            continue
        lowered = candidate.lower()
        if "@" in candidate or "http://" in lowered or "https://" in lowered:
            continue
        if _looks_like_heading(candidate):
            continue
        return candidate
    return None


def _paragraphs(lines: list[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if not line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current).strip())
    return paragraphs


_SUMMARY_LABELS = frozenset({"summary", "profile", "about me"})
_SUMMARY_STOP = frozenset(
    {
        "experience",
        "education",
        "skills",
        "certifications",
        "languages",
        "projects",
        "employment",
    }
)


def extract_summary(text: str) -> str | None:
    if not text:
        return None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower() not in _SUMMARY_LABELS:
            continue
        acc: list[str] = []
        for j in range(i + 1, len(lines)):
            s = lines[j].strip()
            if not s:
                if acc:
                    return " ".join(acc)
                continue
            low = s.lower()
            first_word = low.split()[0] if low.split() else ""
            if low in _SUMMARY_STOP or first_word in _SUMMARY_STOP:
                break
            acc.append(s)
        if acc:
            return " ".join(acc)

    paragraphs = _paragraphs(lines)
    if len(paragraphs) < 2:
        return None
    candidate = paragraphs[1]
    if _starts_with_section_heading(candidate):
        return None
    return candidate


def extract_personal_info(raw_text: str) -> dict[str, str | None]:
    if not raw_text:
        info = PersonalInfo()
        return info.to_dict()

    lines = raw_text.splitlines()
    header_lines = lines[:HEADER_MAX_LINES]
    header_text = "\n".join(header_lines)

    email = extract_email(header_text)
    phone = extract_phone(header_text)
    urls = list(_iter_urls(header_text))
    links = extract_links(header_text)
    name = extract_name(header_lines)
    summary = extract_summary(raw_text)
    website = extract_personal_website(urls, email)
    location = extract_location_from_header(header_lines)

    info = PersonalInfo(
        full_name=name,
        name=name,
        email=email,
        phone=phone,
        linkedin=links.get("linkedin"),
        github=links.get("github"),
        website=website,
        location=location,
        summary=summary,
    )
    return info.to_dict()
