from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp
import pytest

import os
import tempfile


@pytest.fixture
def client():
    db_fd, app.config["DATABASE_URL"] = tempfile.mkstemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE_URL"])


"""
test GET /generate
"""


def test_generate_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/generate", base_url="https://example.com")

    assert res.status_code == 401


def test_generate_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
            session["spotify_wordcloud_text"] = "test1 test2 test3"
            session["spotify_wordcloud_hash"] = "test"
        res = client.get("/generate", base_url="https://example.com")

    assert res.status_code == 200
    assert res.mimetype == "image/png"


"""
test GET /regenerate
"""


def test_regenerate_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/regenerate", base_url="https://example.com")

    assert res.status_code == 401


def test_regenrate_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
            session["spotify_wordcloud_text"] = "test1 test2 test3"
            session["spotify_wordcloud_hash"] = "test"
        res = client.get("/regenerate", base_url="https://example.com")

    assert res.status_code == 200
    assert res.mimetype == "image/png"
