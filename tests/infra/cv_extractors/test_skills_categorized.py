from __future__ import annotations

from src.infra.cv_extractors.skills_categorized import extract_hard_and_soft_skills


def test_extract_hard_and_soft_skills_ignores_empty_lines() -> None:
    hard, soft = extract_hard_and_soft_skills("\n  \nHard skills:\nPython, Go")
    if "Python" not in hard or "Go" not in hard:
        raise AssertionError(f"Expected Python and Go in hard, got {hard!r}")
    if soft != []:
        raise AssertionError(f"Expected empty soft, got {soft!r}")


def test_extract_hard_and_soft_skills_technical_header_treated_as_hard() -> None:
    text = "Technical skills:\nDocker, Kubernetes"
    hard, soft = extract_hard_and_soft_skills(text)
    if "Docker" not in hard or "Kubernetes" not in hard:
        raise AssertionError(f"Expected Docker and Kubernetes in hard, got {hard!r}")
    if soft != []:
        raise AssertionError(f"Expected empty soft, got {soft!r}")
