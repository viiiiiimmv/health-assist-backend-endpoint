from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash

from app.extensions import mongo
from app.models import UserSchema

user_bp = Blueprint("user", __name__)
user_schema = UserSchema()


def _payload():
    return request.get_json(silent=True) or {}


def _sanitize_user(user_doc):
    user_copy = dict(user_doc)
    user_copy["id"] = str(user_copy.get("_id", ""))
    user_copy.pop("password", None)
    return user_schema.dump(user_copy)


@user_bp.route("/register", methods=["POST"])
def register_user():
    data = _payload()
    data.setdefault("auth_provider", "local")

    if data["auth_provider"] != "local":
        return jsonify({"error": "Only local registration is supported"}), 400

    errors = user_schema.validate(data, partial=("id", "created_at"))
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if mongo.db.users.find_one({"email": email, "auth_provider": "local"}):
        return jsonify({"error": "Email already exists"}), 400

    user_doc = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
    }
    result = mongo.db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    return jsonify(_sanitize_user(user_doc)), 201


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(_sanitize_user(user))


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = _payload()
    update_fields = {}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters"}), 400
        update_fields["name"] = name

    if "password" in data:
        password = data.get("password") or ""
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        update_fields["password"] = generate_password_hash(password)

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(_sanitize_user(user))
