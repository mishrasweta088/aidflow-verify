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
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )

    return login_response.json()["access_token"]


def test_admin_can_run_ai_review():
    password = "TestPassword123"
    requester_email = f"ai_requester_{uuid.uuid4()}@test.com"
    admin_email = f"ai_admin_{uuid.uuid4()}@test.com"

    requester_token = register_and_login(requester_email, password, "requester")
    admin_token = register_and_login(admin_email, password, "admin")

    create_response = client.post(
        "/aid-requests",
        headers={"Authorization": f"Bearer {requester_token}"},
        json={
            "title": "Need urgent groceries",
            "description": "Family urgently needs groceries and baby food.",
            "category": "food",
            "address": "Binghamton, NY",
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    aid_request_id = create_response.json()["id"]

    ai_response = client.post(
        f"/aid-requests/{aid_request_id}/ai-review",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response_json = ai_response.json()

    assert ai_response.status_code == 200
    assert response_json["status"] == "ai_reviewed"
    assert response_json["ai_summary"] is not None
    assert response_json["ai_urgency"] is not None
    assert response_json["ai_missing_fields"] is not None
    assert response_json["ai_risk_indicators"] is not None
    assert response_json["ai_verification_checklist"] is not None