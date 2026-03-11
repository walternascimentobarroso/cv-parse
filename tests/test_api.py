from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_extract_missing_file(client: TestClient) -> None:
    response = client.post("/extract")
    # FastAPI may return 422 for missing form field or 400 from our handler
    assert response.status_code in (400, 422)

