import requests
from flask import Flask

from app.services.ml_service import get_prediction


class _DummyResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {"Content-Type": "application/json"}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_ml_service_uses_configured_url_and_includes_history(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return _DummyResponse({"response": "ok", "confidence": 0.7})

    monkeypatch.setattr(requests, "post", fake_post)

    app = Flask(__name__)
    app.config.update(ML_MODEL_URL="http://ml-service.local/predict", ML_MODEL_TIMEOUT=12)

    with app.app_context():
        result = get_prediction("test message", history=[{"sender": "user", "text": "hello"}])

    assert captured["url"] == "http://ml-service.local/predict"
    assert captured["timeout"] == 12
    assert captured["json"]["text"] == "test message"
    assert captured["json"]["history"][0]["sender"] == "user"
    assert result["response"] == "ok"


def test_ml_service_returns_fallback_when_request_fails(monkeypatch):
    def failing_post(url, json, timeout):  # noqa: ARG001
        raise requests.exceptions.RequestException("service unavailable")

    monkeypatch.setattr(requests, "post", failing_post)

    app = Flask(__name__)
    with app.app_context():
        result = get_prediction("test")

    assert "temporarily unavailable" in result["response"]
    assert "error" in result
