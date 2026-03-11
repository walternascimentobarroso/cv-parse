from src.domain.extractor import SimpleDocumentExtractor


def test_plain_text_extraction() -> None:
    extractor = SimpleDocumentExtractor(["text/plain"])
    content = "hello world".encode("utf-8")
    result = extractor.extract(content, "text/plain")
    assert result == "hello world"

