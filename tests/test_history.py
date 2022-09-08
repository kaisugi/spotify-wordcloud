from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.app import db
from spotify_wordcloud.models import Pictures
from spotify_wordcloud.api.auth import spotify_bp
import pytest


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    db.session.query(Pictures).filter(Pictures.user_id == "dummy").delete()
    db.session.commit()


@pytest.fixture
def client_with_dummy_file():
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            record = Pictures(user_id="dummy", file_name="test.png")
            db.session.add(record)
            db.session.commit()
        yield client

    db.session.query(Pictures).filter(Pictures.user_id == "dummy").delete()
    db.session.commit()


# GET /history


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
    assert "test.png" not in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )


def test_history_authorized_with_dummy_file(client_with_dummy_file, monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
        res = client.get("/history", base_url="https://example.com")

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "過去に作成した画像一覧" in text
    assert "まだ画像が保存されていません。" not in text
    assert "test.png" in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )


# DELETE /history/:file_hash


def test_delete(client_with_dummy_file, monkeypatch):
    storage = MemoryStorage({"access_token": "fake-token"})
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = "dummy"
        res1 = client.post(
            "/history/test", base_url="https://example.com", data={"_method": "DELETE"}
        )
        res2 = client.get("/history", base_url="https://example.com")

    assert res1.status_code == 302
    assert res1.headers["Location"] == "/history"

    assert res2.status_code == 200
    text = res2.get_data(as_text=True)
    assert "過去に作成した画像一覧" in text
    assert "まだ画像が保存されていません。" in text
    assert "test.png" not in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )
