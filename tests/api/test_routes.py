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


def test_list_extractions_empty(client: TestClient) -> None:
    response = client.get("/extractions")
    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    data = response.json()
    if "items" not in data:
        raise AssertionError("Expected 'items' in response")
    if not isinstance(data["items"], list):
        raise AssertionError("Expected items to be a list")


def test_get_extraction_not_found_invalid_id(client: TestClient) -> None:
    response = client.get("/extractions/not-a-valid-id")
    if response.status_code != 404:
        raise AssertionError(f"Expected status 404, got {response.status_code}")


def test_get_extraction_not_found_valid_id(client: TestClient) -> None:
    # Valid 24-char hex id that does not exist in the in-memory repo
    response = client.get("/extractions/ffffffffffffffffffffffff")
    if response.status_code != 404:
        raise AssertionError(f"Expected status 404, got {response.status_code}")


def test_crud_extraction_flow(client: TestClient) -> None:
    """Create via POST /extract, then GET by id, list, PATCH, DELETE; soft-deleted not in list."""
    files = {"file": ("test.txt", b"crud test", "text/plain")}
    create_resp = client.post("/extract", files=files)
    if create_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on create, got {create_resp.status_code}")
    body = create_resp.json()
    extraction_id = body["id"]
    if len(extraction_id) != 24:
        raise AssertionError(f"Expected 24-char id, got {extraction_id!r}")

    get_resp = client.get(f"/extractions/{extraction_id}")
    if get_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on GET, got {get_resp.status_code}")
    get_data = get_resp.json()
    if get_data["id"] != extraction_id:
        raise AssertionError(f"Expected id {extraction_id}, got {get_data['id']}")
    if get_data["extracted_text"] != "crud test":
        raise AssertionError(f"Expected extracted_text 'crud test', got {get_data['extracted_text']}")
    if "created_at" not in get_data:
        raise AssertionError("Expected created_at in response")

    list_resp = client.get("/extractions")
    if list_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on list, got {list_resp.status_code}")
    items = list_resp.json()["items"]
    ids = [x["id"] for x in items]
    if extraction_id not in ids:
        raise AssertionError(f"Expected id {extraction_id} in list: {ids}")

    patch_resp = client.patch(
        f"/extractions/{extraction_id}",
        json={"extracted_text": "updated text"},
    )
    if patch_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on PATCH, got {patch_resp.status_code}")
    patch_data = patch_resp.json()
    if patch_data["extracted_text"] != "updated text":
        raise AssertionError(f"Expected updated text, got {patch_data['extracted_text']}")
    if patch_data.get("updated_at") is None:
        raise AssertionError("Expected updated_at after PATCH")

    delete_resp = client.delete(f"/extractions/{extraction_id}")
    if delete_resp.status_code != 204:
        raise AssertionError(f"Expected 204 on DELETE, got {delete_resp.status_code}")

    get_after_resp = client.get(f"/extractions/{extraction_id}")
    if get_after_resp.status_code != 404:
        raise AssertionError(f"Expected 404 after delete, got {get_after_resp.status_code}")

    list_after_resp = client.get("/extractions")
    list_after = list_after_resp.json()["items"]
    ids_after = [x["id"] for x in list_after]
    if extraction_id in ids_after:
        raise AssertionError(f"Soft-deleted id should not be in list: {ids_after}")

    delete_again_resp = client.delete(f"/extractions/{extraction_id}")
    if delete_again_resp.status_code != 404:
        raise AssertionError(f"Expected 404 on second DELETE, got {delete_again_resp.status_code}")
