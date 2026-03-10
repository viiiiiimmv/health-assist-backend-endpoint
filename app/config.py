# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv()

def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}

class BaseConfig:

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/healthchatbot")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "healthchatbot")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-too")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_COOKIE_SECURE = _get_bool("JWT_COOKIE_SECURE", True)

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = os.getenv(
        "GOOGLE_DISCOVERY_URL",
        "https://accounts.google.com/.well-known/openid-configuration",
    )

    ML_MODEL_URL = (
        os.getenv("ML_MODEL_URL")
        or os.getenv("ML_MODEL_URI")  # backward compatibility for older env files
        or "http://localhost:7860/predict"
    )
    ML_MODEL_TIMEOUT = int(os.getenv("ML_MODEL_TIMEOUT", "45"))
    AUTO_CREATE_INDEXES = _get_bool("AUTO_CREATE_INDEXES", False)

    SHARE_BASE_URL = os.getenv("SHARE_BASE_URL", "https://your-domain.com/chat/view/")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class TestingConfig(BaseConfig):
    TESTING = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)

# Map FLASK_ENV / APP_ENV -> config class
ENV_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

def get_config():
    env = os.getenv("APP_ENV") or os.getenv("FLASK_ENV", "development")
    return ENV_MAP.get(env.lower(), DevelopmentConfig)
