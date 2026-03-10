from app import _ensure_mongo_uri_database


def test_ensure_mongo_uri_database_adds_missing_db_for_srv_uri():
    uri = "mongodb+srv://user:pass@cluster.mongodb.net/?appName=HealthAssist"
    normalized_uri, changed = _ensure_mongo_uri_database(uri, "healthchatbot")

    assert changed is True
    assert normalized_uri == "mongodb+srv://user:pass@cluster.mongodb.net/healthchatbot?appName=HealthAssist"


def test_ensure_mongo_uri_database_leaves_existing_db_unchanged():
    uri = "mongodb://localhost:27017/healthchatbot?retryWrites=true"
    normalized_uri, changed = _ensure_mongo_uri_database(uri, "ignored-db")

    assert changed is False
    assert normalized_uri == uri

