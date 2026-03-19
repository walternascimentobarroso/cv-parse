from src.infra.cv_extractors.skills_categorized import extract_hard_and_soft_skills


def test_hard_and_soft_sections() -> None:
    text = """Hard Skills
Python, Docker
Soft Skills
Leadership
"""
    hard, soft = extract_hard_and_soft_skills(text)
    if "Python" not in hard or "Docker" not in hard:
        msg = f"Expected hard skills, got {hard!r}"
        raise AssertionError(msg)
    if "Leadership" not in soft:
        msg = f"Expected soft skills, got {soft!r}"
        raise AssertionError(msg)
