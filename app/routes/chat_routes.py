from datetime import datetime
import re

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import mongo
from app.services.ml_service import get_prediction
from app.utils.link_utils import generate_shareable_link

chat_bp = Blueprint("chat", __name__)
DEFAULT_CHAT_TITLE = "New chat"


def _payload():
    return request.get_json(silent=True) or {}


def _query_id(raw_chat_id):
    try:
        return ObjectId(raw_chat_id)
    except (InvalidId, TypeError):
        return raw_chat_id


def _maybe_object_id(raw_value):
    try:
        return ObjectId(raw_value)
    except (InvalidId, TypeError):
        return None


def _build_user_query(user_id):
    user_query = {"user_id": user_id}
    maybe_oid = _maybe_object_id(user_id)
    if maybe_oid:
        user_query = {"$or": [{"user_id": user_id}, {"user_id": maybe_oid}]}
    return user_query


def _is_owned_by_user(chat_doc, user_id):
    chat_user_id = chat_doc.get("user_id")
    return str(chat_user_id) == str(user_id)


def _truncate(value, max_len=120):
    text = " ".join((value or "").split()).strip()
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3].rstrip()}..."


def _generate_chat_title(text, max_words=8, max_len=64):
    normalized = " ".join((text or "").split()).strip()
    if not normalized:
        return DEFAULT_CHAT_TITLE
    words = normalized.split(" ")[:max_words]
    title = " ".join(words).strip(" .,:;!?-")
    if not title:
        return DEFAULT_CHAT_TITLE
    return _truncate(title, max_len=max_len)


def _derive_chat_title(chat_doc):
    existing = (chat_doc.get("title") or "").strip()
    if existing:
        return existing

    for message in chat_doc.get("messages") or []:
        if message.get("sender") != "user":
            continue
        candidate = _generate_chat_title(message.get("text") or "")
        if candidate != DEFAULT_CHAT_TITLE:
            return candidate
    return DEFAULT_CHAT_TITLE


def _latest_message_preview(messages):
    for message in reversed(messages or []):
        text = (message.get("text") or "").strip()
        if text:
            return _truncate(text)
    return ""


def _chat_to_summary(chat_doc):
    messages = chat_doc.get("messages") or []
    return {
        "chat_id": str(chat_doc["_id"]),
        "created_at": chat_doc.get("created_at"),
        "last_message": _latest_message_preview(messages),
        "title": _derive_chat_title(chat_doc),
        "shareable_link": chat_doc.get("shareable_link"),
        "archived": chat_doc.get("archived", False),
    }


def _chat_to_detail(chat_doc):
    return {
        "chat_id": str(chat_doc["_id"]),
        "user_id": chat_doc.get("user_id"),
        "messages": chat_doc.get("messages", []),
        "created_at": chat_doc.get("created_at"),
        "title": _derive_chat_title(chat_doc),
        "shareable_link": chat_doc.get("shareable_link"),
        "archived": chat_doc.get("archived", False),
        "archived_at": chat_doc.get("archived_at"),
    }


def _readable_history(chat_doc, limit=12):
    history = []
    for msg in (chat_doc.get("messages") or [])[-limit:]:
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        history.append({"sender": msg.get("sender", "user"), "text": text})
    return history


def _split_sentences(text):
    cleaned = " ".join((text or "").split()).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _default_urgent_guidance(triage_level):
    if triage_level == "emergency":
        return (
            "Call emergency services immediately or go to the nearest emergency department now."
        )
    return (
        "Seek urgent care if symptoms worsen quickly, breathing becomes difficult, "
        "severe pain appears, or you feel faint/confused."
    )


def _should_preserve_markdown(text):
    lowered = (text or "").lower()
    has_health_sections = (
        "what this might mean" in lowered
        and "what you can do now" in lowered
        and "when to seek urgent care" in lowered
    )
    if has_health_sections:
        return True

    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    markdownish = any(
        line.startswith(("##", "###", "-", "*", "1.", "2.", "3."))
        or "**" in line
        or "_" in line
        for line in lines
    )
    return markdownish and len(lines) >= 3


def _strip_template_labels(text):
    dropped_labels = {
        "healthassist guidance",
        "what this might mean",
        "what you can do now",
        "when to seek urgent care",
    }
    lines = []
    for raw_line in (text or "").splitlines():
        normalized = raw_line.strip().lower()
        normalized = re.sub(r"^[#>\-*\s]+", "", normalized)
        normalized = re.sub(r"[*_`]+", "", normalized).strip(" :")
        if normalized in dropped_labels:
            continue
        lines.append(raw_line)
    cleaned = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def _rephrase_source_style_language(text):
    cleaned = text or ""
    replacements = [
        (
            r"(the\s+)?information available only covers[^.]*\.",
            "I cannot safely recommend a specific treatment plan from chat alone.",
        ),
        (
            r"there\s+(isn['’]t|is not|isn't)\s+(enough|adequate|sufficient)\s+(reliable\s+)?(context|information)[^.]*\.",
            "I cannot safely recommend a specific treatment plan from chat alone.",
        ),
        (
            r"i\s+(do not|don't|cannot|can't)\s+(have|see)\s+(enough|adequate|sufficient)\s+(medical\s+)?(context|information)[^.]*\.",
            "I cannot safely recommend a specific treatment plan from chat alone.",
        ),
        (
            r"(based on|according to|from)\s+(the\s+)?(provided\s+)?(source|sources|context|documents?)[^.]*\.",
            "",
        ),
    ]

    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\bBecause of (that|this),\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"(I cannot safely recommend a specific treatment plan from chat alone\.\s*){2,}",
        "I cannot safely recommend a specific treatment plan from chat alone. ",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def _rephrase_user_facing_response(text):
    cleaned = _strip_template_labels(text)
    cleaned = _rephrase_source_style_language(cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


def _format_health_chatbot_response(raw_text, triage_level, sources):
    text = (raw_text or "").strip()
    if not text:
        text = "I could not generate a response right now. Please try again."

    # Preserve already-structured markdown from the ML service, then clean labels/phrasing.
    if _should_preserve_markdown(text):
        return _rephrase_user_facing_response(text)

    sentences = _split_sentences(text)
    meaning = sentences[0] if sentences else text

    actions = []
    for sentence in sentences[1:4]:
        actions.append(f"- {sentence}")
    if not actions:
        actions = [
            "- Rest, stay hydrated, and monitor your symptoms over the next 24 hours.",
            "- Track any new symptoms, severity changes, or triggers.",
        ]

    formatted = (
        f"{meaning}\n\n"
        "Try this for now:\n"
        f"{chr(10).join(actions)}\n\n"
        "Get urgent care now if:\n"
        f"{_default_urgent_guidance(triage_level)}\n\n"
        "This is general health information and not a diagnosis."
    )

    return _rephrase_user_facing_response(formatted)


def _load_owned_chat(chat_id, user_id):
    query_id = _query_id(chat_id)
    chat = mongo.db.chats.find_one({"_id": query_id})
    if not chat:
        return None, jsonify({"error": "Chat not found"}), 404
    if not _is_owned_by_user(chat, user_id):
        return None, jsonify({"error": "You are not allowed to access this chat"}), 403
    return chat, None, None


@chat_bp.route("/test-ml", methods=["GET", "POST"])
def test_ml_connection():
    data = _payload()
    text = data.get("text") or request.args.get("text") or "I have a headache"
    result = get_prediction(text)
    return jsonify(result)


@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    user_id = get_jwt_identity()
    include_archived = request.args.get("archived", "false").lower() == "true"

    query = _build_user_query(user_id)
    if not include_archived:
        query["archived"] = {"$ne": True}

    chats_cursor = mongo.db.chats.find(query).sort("created_at", -1)
    chat_list = [_chat_to_summary(chat) for chat in chats_cursor]
    return jsonify({"chats": chat_list})


@chat_bp.route("", methods=["POST"])
@chat_bp.route("/create", methods=["POST"])
@jwt_required()
def create_new_chat():
    user_id = get_jwt_identity()
    link = generate_shareable_link()
    chat_doc = {
        "user_id": user_id,
        "messages": [],
        "created_at": datetime.utcnow(),
        "title": DEFAULT_CHAT_TITLE,
        "shareable_link": link,
        "archived": False,
    }
    result = mongo.db.chats.insert_one(chat_doc)
    return jsonify({"chat_id": str(result.inserted_id), "title": DEFAULT_CHAT_TITLE, "shareable_link": link}), 201


@chat_bp.route("/<chat_id>/message", methods=["POST"])
@jwt_required()
def add_chat_message(chat_id):
    user_id = get_jwt_identity()
    data = _payload()
    user_text = (data.get("text") or "").strip()
    if not user_text:
        return jsonify({"error": "Message text is required"}), 400

    chat, error_response, status = _load_owned_chat(chat_id, user_id)
    if error_response:
        return error_response, status

    user_msg = {
        "sender": "user",
        "text": user_text,
        "timestamp": datetime.utcnow(),
    }

    prediction = get_prediction(user_text, history=_readable_history(chat))
    if isinstance(prediction, dict):
        bot_text = (
            prediction.get("response")
            or prediction.get("answer")
            or "I could not generate a response right now. Please try again."
        )
        confidence = prediction.get("confidence")
        sources = prediction.get("sources") or []
        triage_level = prediction.get("triage_level")
        latency_ms = prediction.get("latency_ms")
        model_used = prediction.get("model_used")
    else:
        bot_text = str(prediction)
        confidence = None
        sources = []
        triage_level = None
        latency_ms = None
        model_used = None

    bot_text = _format_health_chatbot_response(bot_text, triage_level, sources)

    bot_msg = {
        "sender": "bot",
        "text": bot_text,
        "timestamp": datetime.utcnow(),
        "meta": {
            "confidence": confidence,
            "sources": sources,
            "triage_level": triage_level,
            "latency_ms": latency_ms,
            "model_used": model_used,
        },
    }

    updated_title = _derive_chat_title(chat)
    if updated_title == DEFAULT_CHAT_TITLE:
        updated_title = _generate_chat_title(user_text)

    update_doc = {"$push": {"messages": {"$each": [user_msg, bot_msg]}}}
    if updated_title != (chat.get("title") or DEFAULT_CHAT_TITLE):
        update_doc["$set"] = {"title": updated_title}

    mongo.db.chats.update_one(
        {"_id": chat["_id"]},
        update_doc,
    )

    return jsonify(
        {
            "chat_id": str(chat["_id"]),
            "messages": [user_msg, bot_msg],
            "response": bot_text,
            "title": updated_title,
            "confidence": confidence,
            "sources": sources,
            "triage_level": triage_level,
            "latency_ms": latency_ms,
            "model_used": model_used,
            "shareable_link": chat.get("shareable_link"),
        }
    )


@chat_bp.route("/<chat_id>", methods=["GET"])
@jwt_required()
def get_chat_by_id(chat_id):
    user_id = get_jwt_identity()
    chat, error_response, status = _load_owned_chat(chat_id, user_id)
    if error_response:
        return error_response, status
    return jsonify(_chat_to_detail(chat))


@chat_bp.route("/<chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    user_id = get_jwt_identity()
    chat, error_response, status = _load_owned_chat(chat_id, user_id)
    if error_response:
        return error_response, status
    mongo.db.chats.delete_one({"_id": chat["_id"]})
    return jsonify({"message": "Chat deleted successfully"})


@chat_bp.route("/<chat_id>/archive", methods=["POST"])
@jwt_required()
def archive_chat(chat_id):
    user_id = get_jwt_identity()
    chat, error_response, status = _load_owned_chat(chat_id, user_id)
    if error_response:
        return error_response, status
    mongo.db.chats.update_one(
        {"_id": chat["_id"]},
        {"$set": {"archived": True, "archived_at": datetime.utcnow()}},
    )
    return jsonify({"message": "Chat archived successfully"})


@chat_bp.route("/<chat_id>/unarchive", methods=["POST"])
@jwt_required()
def unarchive_chat(chat_id):
    user_id = get_jwt_identity()
    chat, error_response, status = _load_owned_chat(chat_id, user_id)
    if error_response:
        return error_response, status
    mongo.db.chats.update_one(
        {"_id": chat["_id"]},
        {"$set": {"archived": False}, "$unset": {"archived_at": ""}},
    )
    return jsonify({"message": "Chat unarchived successfully"})


@chat_bp.route("/user/<user_id>", methods=["GET"])
@jwt_required()
def get_chats_for_user(user_id):
    requester_id = get_jwt_identity()
    if str(requester_id) != str(user_id):
        return jsonify({"error": "You are not allowed to access these chats"}), 403

    chats = list(mongo.db.chats.find(_build_user_query(user_id)))
    return jsonify({"chats": [_chat_to_summary(chat) for chat in chats]})


@chat_bp.route("/share/<link>", methods=["GET"])
def get_chat_by_shareable_link(link):
    chat = mongo.db.chats.find_one({"shareable_link": link})
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    return jsonify(
        {
            "chat_id": str(chat["_id"]),
            "messages": chat.get("messages", []),
            "created_at": chat.get("created_at"),
            "title": _derive_chat_title(chat),
            "shareable_link": chat.get("shareable_link"),
        }
    )
