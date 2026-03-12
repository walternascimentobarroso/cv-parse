"""API tests for routes (HTTP endpoints). Use TestClient; no real DB or live server."""

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_extract_missing_file(client: TestClient) -> None:
    response = client.post("/extract")
    assert response.status_code == 400
    assert response.json()["detail"] == "Document file is required."


def test_extract_plain_text_success(client: TestClient) -> None:
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "hello world"
    assert body["format"] == "text/plain"
    assert isinstance(body["id"], str)


def test_extract_unsupported_format(client: TestClient) -> None:
    files = {"file": ("image.jpg", b"binary", "image/jpeg")}
    response = client.post("/extract", files=files)

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Unsupported document format." in detail
    assert "Supported formats" in detail


def test_extract_too_large(client: TestClient) -> None:
    # Payload larger than default MAX_DOCUMENT_SIZE_BYTES (10 MB)
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.txt", oversized_content, "text/plain")}
    response = client.post("/extract", files=files)

    assert response.status_code == 413
    assert "Document exceeds maximum allowed size" in response.json()["detail"]


def test_extract_internal_error(client: TestClient) -> None:
    """Override app extractor to force 500; restore after test."""
    class FailingExtractor:
        def extract(self, content: bytes, content_type: str) -> str:
            raise RuntimeError("boom")

    app = client.app
    original = app.state.document_extractor
    app.state.document_extractor = FailingExtractor()
    try:
        files = {"file": ("test.txt", b"hello", "text/plain")}
        response = client.post("/extract", files=files)
        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to process document."
    finally:
        app.state.document_extractor = original
