from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import mongo
from app.models import UserSchema

auth_bp = Blueprint("auth", __name__)
user_schema = UserSchema()


def _payload():
    return request.get_json(silent=True) or {}


def _public_user(user_doc):
    user_copy = dict(user_doc)
    user_copy["id"] = str(user_copy.get("_id", ""))
    user_copy.pop("password", None)
    return user_schema.dump(user_copy)


def _token_response(message, user_doc):
    token = create_access_token(identity=str(user_doc["_id"]))
    return jsonify(
        {
            "message": message,
            "access_token": token,
            "token": token,  # Backward compatibility for older frontend clients.
            "user": _public_user(user_doc),
        }
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = _payload()
    data.setdefault("auth_provider", "local")

    if data["auth_provider"] != "local":
        return jsonify({"error": "Only local registration is allowed on this endpoint"}), 400

    errors = user_schema.validate(data, partial=("id", "created_at"))
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing_user = mongo.db.users.find_one({"email": email, "auth_provider": "local"})
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    new_user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
    }

    result = mongo.db.users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    return (
        jsonify(
            {
                "message": "User registered successfully",
                "user": _public_user(new_user),
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = _payload()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email, "auth_provider": "local"})
    if not user or not user.get("password") or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return _token_response("Login successful", user)


@auth_bp.route("/google", methods=["POST"])
def google_auth():
    data = _payload()
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()

    if not email or not name:
        return jsonify({"error": "Email and name are required"}), 400

    user = mongo.db.users.find_one({"email": email, "auth_provider": "google"})
    if not user:
        new_user = {
            "name": name,
            "email": email,
            "password": None,
            "auth_provider": "google",
            "created_at": datetime.utcnow(),
        }
        result = mongo.db.users.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        user = new_user
        message = "Google user registered"
    else:
        message = "Google login successful"

    return _token_response(message, user), 201 if message == "Google user registered" else 200
