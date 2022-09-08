from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp


# GET /


def test_index_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "よく聴いているアーティストの名前からワードクラウドを作ることができます。" in text
    assert "過去に作成した画像" not in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )


def test_index_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "よく聴いているアーティストの名前からワードクラウドを作ることができます。" not in text
    assert "過去に作成した画像" in text
    assert "ツイートする！" in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )


# GET /login


def test_login(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/login", base_url="https://example.com")

    assert res.status_code == 302
    assert res.headers["Location"] == "/login/spotify"


# GET /logout


def test_logout(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/logout", base_url="https://example.com")

    assert res.status_code == 302
    assert res.headers["Location"] == "/"
