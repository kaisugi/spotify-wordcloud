from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp


def test_index_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/", base_url="https://localhost:5000")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "ワードクラウドを作るアプリです。" in text
    assert "過去に作成した画像" not in text


def test_login(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/login", base_url="https://localhost:5000")

    assert res.status_code == 302
    assert res.headers["Location"] == "https://localhost:5000/login/spotify"
