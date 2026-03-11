from fastapi.testclient import TestClient

from src.api.routes import get_extractor
from src.domain.extractor import SimpleDocumentExtractor
from src.main import app


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
    # Use a payload larger than default MAX_DOCUMENT_SIZE_BYTES (10 MB)
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.txt", oversized_content, "text/plain")}
    response = client.post("/extract", files=files)

    assert response.status_code == 413
    assert "Document exceeds maximum allowed size" in response.json()["detail"]


def test_extract_internal_error(client: TestClient, monkeypatch: object) -> None:
    # Override extractor dependency to force a failure and trigger 500.
    class FailingExtractor:
        def extract(self, content: bytes, content_type: str) -> str:
            raise RuntimeError("boom")

    app.dependency_overrides[get_extractor] = lambda: FailingExtractor()

    files = {"file": ("test.txt", b"hello", "text/plain")}
    response = client.post("/extract", files=files)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process document."

    # Restore a working extractor for any other tests that may run afterwards.
    app.dependency_overrides[get_extractor] = lambda: SimpleDocumentExtractor(
        ["text/plain", "application/pdf"]
    )

