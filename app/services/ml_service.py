import requests
from flask import current_app

ML_MODEL_URI = "https://shivchauhan-health-assist-ml-service.hf.space/predict"


def get_prediction(text: str, history=None):
    """Send text + recent history to ML server and return JSON payload."""
    url = current_app.config.get("ML_MODEL_URL", ML_MODEL_URI)
    timeout = current_app.config.get("ML_MODEL_TIMEOUT", 45)
    payload = {"text": text}
    if history:
        payload["history"] = history

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        if "application/json" in resp.headers.get("Content-Type", ""):
            return resp.json()
        return {"response": resp.text.strip() or "The ML service returned an empty response."}
    except requests.exceptions.RequestException as e:
        return {
            "response": "The AI assistant is temporarily unavailable. Please try again shortly.",
            "error": str(e),
        }
