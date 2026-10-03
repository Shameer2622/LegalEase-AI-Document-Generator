from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_generate_validation():
    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "A, B",
            "terms": "Confidentiality",
            "effective_date": "October 10, 2026",
        },
    )
    assert response.status_code == 422
