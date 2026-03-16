"""API tests for routes (HTTP endpoints). Use TestClient; no real DB or live server."""

from fastapi.testclient import TestClient

from src.api.dependencies import get_extractor
from src.infra.config import Settings
from src.services.upload_validator import ValidationOk


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


def test_extract_zero_size_short_circuits(client: TestClient, monkeypatch: object) -> None:
    """When validator returns size_bytes == 0, route should return empty ExtractResponse."""

    async def fake_validate_upload(file, settings: Settings) -> ValidationOk:  # type: ignore[override]
        return ValidationOk(
            content=b"",
            content_type="text/plain",
            filename="empty.txt",
            size_bytes=0,
        )

    import src.api.routes as routes_module

    monkeypatch.setattr(routes_module, "validate_upload", fake_validate_upload)

    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/extract", files=files)
    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    body = response.json()
    if body["text"] != "":
        raise AssertionError(f"Expected empty text, got {body['text']!r}")
    if body["id"] != "":
        raise AssertionError(f"Expected empty id for zero-size, got {body['id']!r}")


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


def test_restore_soft_deleted_extraction(client: TestClient) -> None:
    files = {"file": ("test.txt", b"restore test", "text/plain")}
    create_resp = client.post("/extract", files=files)
    if create_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on create, got {create_resp.status_code}")
    extraction_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/extractions/{extraction_id}")
    if delete_resp.status_code != 204:
        raise AssertionError(f"Expected 204 on DELETE, got {delete_resp.status_code}")

    restore_resp = client.post(f"/extractions/{extraction_id}/restore")
    if restore_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on restore, got {restore_resp.status_code}")
    restored = restore_resp.json()
    if restored["id"] != extraction_id:
        raise AssertionError(f"Expected restored id {extraction_id}, got {restored['id']}")
    if restored.get("deleted_at") is not None:
        raise AssertionError("Expected deleted_at to be null after restore")


def test_restore_non_deleted_extraction_returns_400(client: TestClient) -> None:
    files = {"file": ("test.txt", b"not deleted", "text/plain")}
    create_resp = client.post("/extract", files=files)
    if create_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on create, got {create_resp.status_code}")
    extraction_id = create_resp.json()["id"]

    restore_resp = client.post(f"/extractions/{extraction_id}/restore")
    if restore_resp.status_code != 400:
        raise AssertionError(f"Expected 400 when restoring non-deleted record, got {restore_resp.status_code}")


def test_force_delete_extraction(client: TestClient) -> None:
    files = {"file": ("test.txt", b"force delete", "text/plain")}
    create_resp = client.post("/extract", files=files)
    if create_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on create, got {create_resp.status_code}")
    extraction_id = create_resp.json()["id"]

    force_resp = client.delete(f"/extractions/{extraction_id}/force")
    if force_resp.status_code != 204:
        raise AssertionError(f"Expected 204 on force delete, got {force_resp.status_code}")

    get_after_resp = client.get(f"/extractions/{extraction_id}")
    if get_after_resp.status_code != 404:
        raise AssertionError(f"Expected 404 after force delete, got {get_after_resp.status_code}")

    restore_after_resp = client.post(f"/extractions/{extraction_id}/restore")
    if restore_after_resp.status_code != 404:
        raise AssertionError(f"Expected 404 when restoring force-deleted record, got {restore_after_resp.status_code}")


def test_update_extraction_invalid_id_returns_404(client: TestClient) -> None:
    response = client.patch("/extractions/not-a-valid-id", json={"extracted_text": "x"})
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 for invalid id, got {response.status_code}")


def test_update_extraction_empty_body_uses_existing_document(client: TestClient) -> None:
    files = {"file": ("test.txt", b"unchanged", "text/plain")}
    create_resp = client.post("/extract", files=files)
    if create_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on create, got {create_resp.status_code}")
    extraction_id = create_resp.json()["id"]

    patch_resp = client.patch(f"/extractions/{extraction_id}", json={})
    if patch_resp.status_code != 200:
        raise AssertionError(f"Expected 200 on PATCH with empty body, got {patch_resp.status_code}")
    data = patch_resp.json()
    if data["id"] != extraction_id:
        raise AssertionError(f"Expected same id in response, got {data['id']!r}")


def test_update_extraction_not_found_after_valid_id(client: TestClient, monkeypatch: object) -> None:
    """Simulate repo.update returning None to exercise 404 branch."""
    app = client.app
    repo = app.state.extraction_repo

    async def fake_update(extraction_id: str, payload: dict):  # type: ignore[override]
        return None

    original_update = repo.update
    repo.update = fake_update  # type: ignore[assignment]
    try:
        response = client.patch(
            "/extractions/ffffffffffffffffffffffff",
            json={"extracted_text": "x"},
        )
        if response.status_code != 404:
            raise AssertionError(f"Expected 404 when repo.update returns None, got {response.status_code}")
    finally:
        repo.update = original_update  # type: ignore[assignment]


def test_delete_extraction_invalid_id_returns_404(client: TestClient) -> None:
    response = client.delete("/extractions/not-a-valid-id")
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 for invalid id, got {response.status_code}")


def test_update_extraction_empty_body_not_found_returns_404(client: TestClient) -> None:
    """Empty body with non-existent but valid id should yield 404."""
    response = client.patch("/extractions/ffffffffffffffffffffffff", json={})
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 when empty body and document not found, got {response.status_code}")


def test_restore_invalid_id_returns_404(client: TestClient) -> None:
    response = client.post("/extractions/not-a-valid-id/restore")
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 for invalid id on restore, got {response.status_code}")


def test_restore_not_found_returns_404(client: TestClient) -> None:
    response = client.post("/extractions/ffffffffffffffffffffffff/restore")
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 when restoring non-existent id, got {response.status_code}")


def test_restore_404_when_document_missing_after_restore(client: TestClient, monkeypatch: object) -> None:
    """Simulate repo.restore succeeding but repo.find_by_id returning None."""
    app = client.app
    repo = app.state.extraction_repo

    async def fake_restore(extraction_id: str) -> str:  # type: ignore[override]
        return "restored"

    async def fake_find_by_id(extraction_id: str) -> None:  # type: ignore[override]
        return None

    original_restore = repo.restore
    original_find_by_id = repo.find_by_id
    repo.restore = fake_restore  # type: ignore[assignment]
    repo.find_by_id = fake_find_by_id  # type: ignore[assignment]
    try:
        response = client.post("/extractions/ffffffffffffffffffffffff/restore")
        if response.status_code != 404:
            raise AssertionError(
                f"Expected 404 when repo.find_by_id returns None after restore, got {response.status_code}",
            )
    finally:
        repo.restore = original_restore  # type: ignore[assignment]
        repo.find_by_id = original_find_by_id  # type: ignore[assignment]


def test_force_delete_invalid_id_returns_404(client: TestClient) -> None:
    response = client.delete("/extractions/not-a-valid-id/force")
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 for invalid id on force delete, got {response.status_code}")


def test_force_delete_not_found_returns_404(client: TestClient) -> None:
    response = client.delete("/extractions/ffffffffffffffffffffffff/force")
    if response.status_code != 404:
        raise AssertionError(f"Expected 404 for non-existent id on force delete, got {response.status_code}")
