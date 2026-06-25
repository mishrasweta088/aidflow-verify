import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def register_and_login(email: str, password: str, role: str) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "role": role,
            "full_name": f"Test {role}",
            "phone": "1234567890",
            "address": "Binghamton, NY",
            "latitude": 42.1000,
            "longitude": -75.9200,
        },
    )

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    return login_response.json()["access_token"]


def test_admin_can_find_nearby_volunteers():
    password = "TestPassword123"

    requester_token = register_and_login(
        f"matching_requester_{uuid.uuid4()}@test.com",
        password,
        "requester",
    )

    admin_token = register_and_login(
        f"matching_admin_{uuid.uuid4()}@test.com",
        password,
        "admin",
    )

    register_and_login(
        f"matching_volunteer_{uuid.uuid4()}@test.com",
        password,
        "volunteer",
    )

    create_response = client.post(
        "/aid-requests",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "title": "Need food support",
            "description": "Need food support near Binghamton.",
            "category": "food",
            "address": "Binghamton, NY",
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    aid_request_id = create_response.json()["id"]

    nearby_response = client.get(
        f"/aid-requests/{aid_request_id}/nearby-volunteers",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response_json = nearby_response.json()

    assert nearby_response.status_code == 200
    assert len(response_json) >= 1
    assert response_json[0]["email"] is not None
    assert response_json[0]["distance_meters"] is not None