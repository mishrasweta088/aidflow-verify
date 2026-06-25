import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login_requester():
    unique_email = f"test_requester_{uuid.uuid4()}@test.com"
    password = "TestPassword123"

    register_response = client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": password,
            "role": "requester",
            "full_name": "Test Requester",
            "phone": "1234567890",
            "address": "Binghamton, NY",
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == unique_email
    assert register_response.json()["role"] == "requester"

    login_response = client.post(
        "/auth/login",
        data={
            "username": unique_email,
            "password": password,
        },
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"
    
def test_requester_cannot_approve_request():
    unique_email = f"rbac_requester_{uuid.uuid4()}@test.com"
    password = "TestPassword123"

    client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": password,
            "role": "requester",
            "full_name": "RBAC Requester",
            "phone": "1234567890",
            "address": "Binghamton, NY",
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    login_response = client.post(
        "/auth/login",
        data={"username": unique_email, "password": password},
    )

    token = login_response.json()["access_token"]

    create_response = client.post(
        "/aid-requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Need test food",
            "description": "Need food for RBAC test.",
            "category": "food",
            "address": "Binghamton, NY",
            "latitude": 42.0987,
            "longitude": -75.9180,
        },
    )

    aid_request_id = create_response.json()["id"]

    approve_response = client.post(
        f"/aid-requests/{aid_request_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert approve_response.status_code == 403