from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_application():
    payload = {
        "student_id": "00000000-0000-0000-0000-000000000001",
        "scheme_id": "PRE_MATRIC",
    }

    response = client.post("/api/v1/applications", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["student_id"] == payload["student_id"]
    assert data["scheme_id"] == "PRE_MATRIC"
    assert data["status"] == "SUBMITTED"


def test_get_application():
    payload = {
        "student_id": "00000000-0000-0000-0000-000000000002",
        "scheme_id": "POST_MATRIC",
    }

    create_response = client.post("/api/v1/applications", json=payload)
    application_id = create_response.json()["id"]

    response = client.get(f"/api/v1/applications/{application_id}")

    assert response.status_code == 200
    assert response.json()["id"] == application_id


def test_get_unknown_application():
    response = client.get(
        "/api/v1/applications/00000000-0000-0000-0000-000000000999"
    )

    assert response.status_code == 404


def test_invalid_student_id():
    payload = {
        "student_id": "not-a-uuid",
        "scheme_id": "PRE_MATRIC",
    }

    response = client.post("/api/v1/applications", json=payload)

    assert response.status_code == 422


def test_invalid_scheme_id():
    payload = {
        "student_id": "00000000-0000-0000-0000-000000000003",
        "scheme_id": "INVALID_SCHEME",
    }

    response = client.post("/api/v1/applications", json=payload)

    assert response.status_code == 422

