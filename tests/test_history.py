from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp
import pytest

import os
import tempfile


@pytest.fixture
def client():
    db_fd, app.config["SQLALCHEMY_DATABASE_URI"] = tempfile.mkstemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config["SQLALCHEMY_DATABASE_URI"])


"""
test GET /history
"""


def test_history_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/history", base_url="https://example.com")

    assert res.status_code == 401


def test_history_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
        res = client.get("/history", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "過去に作成した画像一覧" in text
    assert "まだ画像が保存されていません。" in text
