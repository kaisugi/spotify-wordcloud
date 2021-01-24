from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp


"""
test GET /
"""


def test_index_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "例えば、こんなワードクラウドが作れます。" in text
    assert "過去に作成した画像" not in text


def test_index_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "例えば、こんなワードクラウドが作れます。" not in text
    assert "過去に作成した画像" in text
    assert "ツイートする！" not in text


def test_index_authorized_with_twitter(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["oauth_verifier"] = "dummy"
        res = client.get("/", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "例えば、こんなワードクラウドが作れます。" not in text
    assert "過去に作成した画像" in text
    assert "ツイートする！" in text


"""
test GET /
"""


def test_login(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/login", base_url="https://example.com")

    assert res.status_code == 302
    assert res.headers["Location"] == "https://example.com/login/spotify"


"""
test GET /twitter_auth
"""


def test_twitter_auth_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/twitter_auth", base_url="https://example.com")

    assert res.status_code == 401


def test_twitter_auth_authorized(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/twitter_auth", base_url="https://example.com")

    assert res.status_code == 302


"""
test GET /logout
"""


def test_logout(monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/logout", base_url="https://example.com")

    assert res.status_code == 302
    assert res.headers["Location"] == "https://example.com/"
