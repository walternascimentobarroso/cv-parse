from src.infra.cv_extractors.languages_extractor import extract_languages


def test_languages_name_level() -> None:
    text = """English - Native
French: Professional
"""
    r = extract_languages(text)
    if len(r) < 2:
        raise AssertionError(f"Expected 2 languages, got {r!r}")
    en = next(x for x in r if x["name"] == "English")
    if en.get("level") != "Native":
        raise AssertionError(f"Expected Native, got {en!r}")
