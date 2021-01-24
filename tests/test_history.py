from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.app import db
from spotify_wordcloud.api.auth import spotify_bp
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


"""
test GET /history
"""


def test_history_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/history", base_url="https://example.com")

    assert res.status_code == 401


def test_history_authorized(client, monkeypatch):
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
