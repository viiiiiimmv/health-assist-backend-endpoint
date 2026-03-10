import logging
from urllib.parse import urlsplit, urlunsplit

from flask import Flask
from .config import get_config
from .extensions import mongo, jwt, oauth
from flask_cors import CORS

from .main import main_bp
from .routes.auth_routes import auth_bp
from .routes.chat_routes import chat_bp
from .routes.user_routes import user_bp


def _normalized_api_prefix(raw_prefix):
    prefix = (raw_prefix or "").strip()
    if not prefix:
        return ""
    return "/" + prefix.strip("/")


def _parse_cors_origins(raw_origins):
    if isinstance(raw_origins, list):
        return raw_origins
    if not isinstance(raw_origins, str):
        return "*"
    value = raw_origins.strip()
    if not value:
        return "*"
    if value == "*":
        return "*"
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def _normalize_db_name(raw_name):
    return str(raw_name or "").strip().strip("/")


def _ensure_mongo_uri_database(raw_uri, fallback_db_name):
    uri = (raw_uri or "").strip()
    db_name = _normalize_db_name(fallback_db_name)

    if not uri or not db_name:
        return raw_uri, False

    parsed = urlsplit(uri)
    if parsed.scheme not in {"mongodb", "mongodb+srv"}:
        return uri, False

    if parsed.path and parsed.path.strip("/"):
        return uri, False

    normalized_uri = urlunsplit(parsed._replace(path=f"/{db_name}"))
    return normalized_uri, normalized_uri != uri


def _register_with_api_alias(app, blueprint, url_prefix):
    app.register_blueprint(blueprint, url_prefix=url_prefix)
    api_prefix = _normalized_api_prefix(app.config.get("API_PREFIX", "/api"))
    if api_prefix:
        alias_prefix = f"{api_prefix}{url_prefix}"
        app.register_blueprint(
            blueprint,
            url_prefix=alias_prefix,
            name=f"api_{blueprint.name}",
        )


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)

    app.config.from_object(get_config())

    normalized_mongo_uri, mongo_uri_changed = _ensure_mongo_uri_database(
        app.config.get("MONGO_URI"),
        app.config.get("MONGO_DB_NAME"),
    )
    if normalized_mongo_uri:
        app.config["MONGO_URI"] = normalized_mongo_uri
    if mongo_uri_changed:
        app.logger.warning(
            "MONGO_URI had no database name; defaulting to '%s'.",
            app.config.get("MONGO_DB_NAME"),
        )

    mongo.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)

    google_client_id = app.config.get("GOOGLE_CLIENT_ID")
    google_client_secret = app.config.get("GOOGLE_CLIENT_SECRET")
    if google_client_id and google_client_secret:
        oauth.register(
            name="google",
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
            client_kwargs={"scope": "openid email profile"},
        )
    else:
        app.logger.info("Google OAuth is disabled (missing client credentials).")

    _register_with_api_alias(app, main_bp, "")
    _register_with_api_alias(app, auth_bp, "/auth")
    _register_with_api_alias(app, chat_bp, "/chat")
    _register_with_api_alias(app, user_bp, "/user")

    cors_origins = _parse_cors_origins(app.config.get("CORS_ORIGINS", "*"))
    supports_credentials = cors_origins != "*"
    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=supports_credentials,
    )

    app.logger.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO))

    if app.config.get("AUTO_CREATE_INDEXES"):
        try:
            mongo.db.users.create_index(
                [("email", 1), ("auth_provider", 1)],
                unique=True,
            )
            mongo.db.chats.create_index([("user_id", 1), ("created_at", -1)])
            mongo.db.chats.create_index("shareable_link", unique=True)
        except Exception as exc:  # pragma: no cover - DB unavailability should not crash startup
            app.logger.warning("Skipping DB index initialization: %s", exc)

    return app
