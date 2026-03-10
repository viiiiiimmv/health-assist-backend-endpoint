import copy
import os
import sys
from dataclasses import dataclass

import pytest
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import mongo


@dataclass
class _InsertResult:
    inserted_id: ObjectId


class _FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, field, direction):
        reverse = direction == -1
        sorted_docs = sorted(
            self._docs,
            key=lambda doc: doc.get(field),
            reverse=reverse,
        )
        return _FakeCursor(sorted_docs)

    def __iter__(self):
        for doc in self._docs:
            yield copy.deepcopy(doc)


class _FakeCollection:
    def __init__(self):
        self.docs = []

    def create_index(self, *args, **kwargs):  # pragma: no cover - index is a startup concern
        return None

    def _matches(self, doc, query):
        for key, value in query.items():
            doc_value = doc.get(key)
            if isinstance(value, dict):
                if "$ne" in value:
                    if doc_value == value["$ne"]:
                        return False
                else:
                    return False
            else:
                if doc_value != value:
                    return False
        return True

    def find_one(self, query):
        for doc in self.docs:
            if self._matches(doc, query):
                return copy.deepcopy(doc)
        return None

    def find(self, query):
        filtered = [doc for doc in self.docs if self._matches(doc, query)]
        return _FakeCursor(copy.deepcopy(filtered))

    def insert_one(self, doc):
        inserted = copy.deepcopy(doc)
        inserted["_id"] = ObjectId()
        self.docs.append(inserted)
        return _InsertResult(inserted_id=inserted["_id"])

    def update_one(self, query, update):
        for idx, existing in enumerate(self.docs):
            if not self._matches(existing, query):
                continue

            updated = copy.deepcopy(existing)
            for field, value in update.get("$set", {}).items():
                updated[field] = value

            for field in update.get("$unset", {}).keys():
                updated.pop(field, None)

            for field, value in update.get("$push", {}).items():
                updated.setdefault(field, [])
                if isinstance(value, dict) and "$each" in value:
                    updated[field].extend(value["$each"])
                else:
                    updated[field].append(value)

            self.docs[idx] = updated
            return

    def delete_one(self, query):
        for idx, doc in enumerate(self.docs):
            if self._matches(doc, query):
                self.docs.pop(idx)
                return


class _FakeDB:
    def __init__(self):
        self.users = _FakeCollection()
        self.chats = _FakeCollection()


@pytest.fixture
def fake_db(monkeypatch):
    db = _FakeDB()
    return db


@pytest.fixture
def client(fake_db, monkeypatch):
    monkeypatch.setattr(
        "app.routes.chat_routes.get_prediction",
        lambda text, history=None: {
            "response": f"Mocked response for: {text}",
            "confidence": 0.9,
            "sources": ["medical_book.pdf"],
            "triage_level": "routine",
        },
    )

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
    )
    monkeypatch.setattr(mongo, "db", fake_db, raising=False)

    with app.test_client() as test_client:
        yield test_client
