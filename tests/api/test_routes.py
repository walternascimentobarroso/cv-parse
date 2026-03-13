"""API tests for routes (HTTP endpoints). Use TestClient; no real DB or live server."""

from fastapi.testclient import TestClient

from src.api.dependencies import get_extractor


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
        raise AssertionError(f"Expected 'Document file is required.', got {response.json()['detail']}")


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
    # Payload larger than default MAX_DOCUMENT_SIZE_BYTES (10 MB)
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)
    files = {"file": ("big.txt", oversized_content, "text/plain")}
    response = client.post("/extract", files=files)

    if response.status_code != 413:
        raise AssertionError(f"Expected status 413, got {response.status_code}")
    if "Document exceeds maximum allowed size" not in response.json()["detail"]:
        raise AssertionError(f"Expected size error in detail: {response.json()['detail']}")


def test_extract_internal_error(client: TestClient) -> None:
    """Use dependency override to inject failing extractor; assert 500 and detail."""

    class FailingExtractor:
        def extract(self, content: bytes, content_type: str) -> str:
            raise RuntimeError("boom")

    def override_extractor():
        return FailingExtractor()

    app = client.app
    app.dependency_overrides[get_extractor] = override_extractor
    try:
        files = {"file": ("test.txt", b"hello", "text/plain")}
        response = client.post("/extract", files=files)
        if response.status_code != 500:
            raise AssertionError(f"Expected status 500, got {response.status_code}")
        if response.json()["detail"] != "Failed to process document.":
            raise AssertionError(f"Expected 'Failed to process document.', got {response.json()['detail']}")
    finally:
        app.dependency_overrides.pop(get_extractor, None)
