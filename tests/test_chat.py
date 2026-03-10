def _register_and_login(client, email):
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": email.split("@")[0],
            "email": email,
            "password": "password123",
            "auth_provider": "local",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_create_alias_and_message_flow(client):
    headers = _register_and_login(client, "chat_owner@example.com")

    create_response = client.post("/api/chat", headers=headers)
    assert create_response.status_code == 201
    created = create_response.get_json()
    chat_id = created["chat_id"]
    assert created["shareable_link"]

    message_response = client.post(
        f"/api/chat/{chat_id}/message",
        headers=headers,
        json={"text": "I have a mild headache"},
    )
    assert message_response.status_code == 200
    message_body = message_response.get_json()
    assert "HealthAssist Guidance" not in message_body["response"]
    assert "What this might mean" not in message_body["response"]
    assert "Try this for now:" in message_body["response"]
    assert "Get urgent care now if:" in message_body["response"]
    assert message_body["messages"][0]["sender"] == "user"
    assert message_body["messages"][1]["sender"] == "bot"
    assert "HealthAssist Guidance" not in message_body["messages"][1]["text"]
    assert message_body["confidence"] == 0.9


def test_chat_access_is_restricted_to_owner(client):
    owner_headers = _register_and_login(client, "owner@example.com")
    other_headers = _register_and_login(client, "other@example.com")

    create_response = client.post("/api/chat", headers=owner_headers)
    chat_id = create_response.get_json()["chat_id"]

    unauthorized_read = client.get(f"/api/chat/{chat_id}", headers=other_headers)
    assert unauthorized_read.status_code == 403

    unauthorized_delete = client.delete(f"/api/chat/{chat_id}", headers=other_headers)
    assert unauthorized_delete.status_code == 403


def test_test_ml_endpoint_accepts_post_payload(client):
    response = client.post("/api/chat/test-ml", json={"text": "fever and cough"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["response"].startswith("Mocked response for:")


def test_chat_preserves_markdown_from_ml_response(client, monkeypatch):
    def _mock_prediction(_text, history=None):
        assert history is not None
        return {
            "response": (
                "## HealthAssist Guidance\n\n"
                "**What this might mean**\n"
                "This pattern can happen with mild dehydration.\n\n"
                "**What you can do now**\n"
                "- Drink water regularly.\n"
                "- Rest for the next few hours.\n\n"
                "**When to seek urgent care**\n"
                "Go to urgent care if dizziness becomes severe or persistent.\n\n"
                "*I can help you track symptoms over the next day.*"
            ),
            "confidence": 0.88,
            "sources": ["clinic_guide.pdf"],
            "triage_level": "routine",
        }

    monkeypatch.setattr("app.routes.chat_routes.get_prediction", _mock_prediction)
    headers = _register_and_login(client, "markdown_owner@example.com")

    create_response = client.post("/api/chat", headers=headers)
    chat_id = create_response.get_json()["chat_id"]
    message_response = client.post(
        f"/api/chat/{chat_id}/message",
        headers=headers,
        json={"text": "I feel dizzy"},
    )

    assert message_response.status_code == 200
    body = message_response.get_json()
    assert "HealthAssist Guidance" not in body["response"]
    assert "What this might mean" not in body["response"]
    assert "- Drink water regularly." in body["response"]
    assert "**Based on:**" not in body["response"]
    assert body["sources"] == ["clinic_guide.pdf"]


def test_chat_rephrases_source_context_language(client, monkeypatch):
    def _mock_prediction(_text, history=None):
        assert history is not None
        return {
            "response": (
                "The information available only covers some alternative approaches for allergic rhinitis (AR), "
                "not for nausea, cough, or fever. Because of that, there isn't enough reliable context here "
                "to safely suggest specific home remedies for your current symptoms."
            ),
            "confidence": 0.77,
            "sources": ["medical_book.pdf"],
            "triage_level": "routine",
        }

    monkeypatch.setattr("app.routes.chat_routes.get_prediction", _mock_prediction)
    headers = _register_and_login(client, "paraphrase_owner@example.com")

    create_response = client.post("/api/chat", headers=headers)
    chat_id = create_response.get_json()["chat_id"]
    message_response = client.post(
        f"/api/chat/{chat_id}/message",
        headers=headers,
        json={"text": "Can I use home remedies for nausea, cough and fever?"},
    )

    assert message_response.status_code == 200
    body = message_response.get_json()
    lowered = body["response"].lower()
    assert "information available only covers" not in lowered
    assert "reliable context" not in lowered
    assert "source" not in lowered
    assert "i cannot safely recommend a specific treatment plan from chat alone." in lowered
