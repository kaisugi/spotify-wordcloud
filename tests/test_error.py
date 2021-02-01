from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp


def test_error(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get("/sonzaishinai", base_url="https://example.com")

    assert res.status_code == 404
    text = res.get_data(as_text=True)
    assert "このページはすでに削除されているか、URLが間違っている可能性があります。" in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        in text
    )
