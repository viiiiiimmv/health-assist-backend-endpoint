def test_register_and_login_returns_access_token_contract(client):
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "auth_provider": "local",
    }
    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    body = login_response.get_json()
    assert "access_token" in body
    assert "token" in body
    assert body["access_token"] == body["token"]
    assert body["user"]["email"] == "test@example.com"


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Weak Pass",
            "email": "weak@example.com",
            "password": "short",
            "auth_provider": "local",
        },
    )
    assert response.status_code == 400
    assert "Password must be at least 8 characters" in response.get_json()["error"]
