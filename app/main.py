import os

from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Health Chatbot Backend is running ✅"}), 200

@main_bp.route("/health", methods=["GET"])
def health_check():
    return (
        jsonify(
            {
                "status": "ok",
                "service": "health-assist-backend",
                "env": os.getenv("APP_ENV", "development"),
            }
        ),
        200,
    )
