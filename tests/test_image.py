from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.app import db
from spotify_wordcloud.models import Pictures
from spotify_wordcloud.api.auth import spotify_bp
import pytest
import json


@pytest.fixture
def client():
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    db.session.query(Pictures).filter(Pictures.user_id == "dummy").delete()
    db.session.commit()


# GET /generate


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


# GET /regenerate


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


# POST /save


def test_save_unauthorized(client, monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.post("/save", base_url="https://example.com")

    assert res.status_code == 401


def test_save_authorized(client, monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
            session["spotify_wordcloud_text"] = "test1 test2 test3"
            session["spotify_wordcloud_hash"] = "test"
        res0 = client.get("/history", base_url="https://example.com")
        res1 = client.post("/save", base_url="https://example.com")
        res2 = client.get("/history", base_url="https://example.com")

    assert res0.status_code == 200
    text = res0.get_data(as_text=True)
    assert "過去に作成した画像一覧" in text
    assert "まだ画像が保存されていません。" in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )

    assert res1.status_code == 200

    assert res2.status_code == 200
    text = res2.get_data(as_text=True)
    assert "過去に作成した画像一覧" in text
    assert "まだ画像が保存されていません。" not in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )


# GET /shareLink


def test_share_link_unauthorized(client, monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/shareLink", base_url="https://example.com")

    assert res.status_code == 401


def test_share_link_authorized(client, monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
            session["spotify_wordcloud_text"] = "test1 test2 test3"
            session["spotify_wordcloud_hash"] = "test"
        client.get("/generate", base_url="https://example.com")
        res0 = client.get("/shareLink", base_url="https://example.com")
        client.get("/generate", base_url="https://example.com")
        res1 = client.get("/shareLink", base_url="https://example.com")
        client.get("/regenerate", base_url="https://example.com")
        res2 = client.get("/shareLink", base_url="https://example.com")

    assert res0.status_code == 200
    assert res1.status_code == 200
    assert res2.status_code == 200
    data0 = json.loads(res0.get_data(as_text=True))
    data1 = json.loads(res1.get_data(as_text=True))
    data2 = json.loads(res2.get_data(as_text=True))
    assert data0["link"] == data1["link"]
    assert data0["link"] != data2["link"]


# POST /shareTwitter


def test_share_twitter_unauthorized(client, monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.post("/shareTwitter", base_url="https://example.com")

    assert res.status_code == 401


def test_share_twitter_authorized(client, monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
            session["spotify_wordcloud_text"] = "test1 test2 test3"
            session["spotify_wordcloud_hash"] = "test"
        res = client.post("/shareTwitter", base_url="https://example.com")

    assert res.status_code == 302
    assert res.headers["Location"].startswith("https://twitter.com/")
