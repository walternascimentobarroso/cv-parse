from fastapi.testclient import TestClient

from src.api.routes import get_extractor
from src.domain.extractor import SimpleDocumentExtractor
from src.main import app


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    if response.json().get("status") != "ok":
        raise AssertionError(f"Expected status 'ok', got {response.json().get('status')}")


def test_extract_missing_file(client: TestClient) -> None:
    response = client.post("/extract")
    if response.status_code != 400:
        raise AssertionError(f"Expected status 400, got {response.status_code}")
    if response.json()["detail"] != "Document file is required.":
        raise AssertionError(
            f"Expected detail 'Document file is required.', got {response.json()['detail']}"
        )


def test_extract_plain_text_success(client: TestClient) -> None:
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/extract", files=files)

    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    body = response.json()
    if body["text"] != "hello world":
        raise AssertionError(f"Expected text 'hello world', got {body['text']}")
    if body["format"] != "text/plain":
        raise AssertionError(f"Expected format 'text/plain', got {body['format']}")
    if not isinstance(body["id"], str):
        raise AssertionError(f"Expected id to be str, got {type(body['id'])}")


def test_extract_unsupported_format(client: TestClient) -> None:
    files = {"file": ("image.jpg", b"binary", "image/jpeg")}
    response = client.post("/extract", files=files)

    if response.status_code != 400:
        raise AssertionError(f"Expected status 400, got {response.status_code}")
    detail = response.json()["detail"]
    if "Unsupported document format." not in detail:
        raise AssertionError(f"Expected 'Unsupported document format.' in detail: {detail}")
    if "Supported formats" not in detail:
        raise AssertionError(f"Expected 'Supported formats' in detail: {detail}")


def test_extract_too_large(client: TestClient) -> None:
    # Use a payload larger than default MAX_DOCUMENT_SIZE_BYTES (10 MB)
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.txt", oversized_content, "text/plain")}
    response = client.post("/extract", files=files)

    if response.status_code != 413:
        raise AssertionError(f"Expected status 413, got {response.status_code}")
    if "Document exceeds maximum allowed size" not in response.json()["detail"]:
        raise AssertionError(
            f"Expected 'Document exceeds maximum allowed size' in detail: {response.json()['detail']}"
        )


def test_extract_internal_error(client: TestClient, monkeypatch: object) -> None:
    # Override extractor dependency to force a failure and trigger 500.
    class FailingExtractor:
        def extract(self, content: bytes, content_type: str) -> str:
            raise RuntimeError("boom")

    def _failing_extractor():
        return FailingExtractor()

    app.dependency_overrides[get_extractor] = _failing_extractor

    files = {"file": ("test.txt", b"hello", "text/plain")}
    response = client.post("/extract", files=files)
    if response.status_code != 500:
        raise AssertionError(f"Expected status 500, got {response.status_code}")
    if response.json()["detail"] != "Failed to process document.":
        raise AssertionError(
            f"Expected detail 'Failed to process document.', got {response.json()['detail']}"
        )

    # Restore a working extractor for any other tests that may run afterwards.
    def _default_extractor():
        return SimpleDocumentExtractor(["text/plain", "application/pdf"])

    app.dependency_overrides[get_extractor] = _default_extractor

