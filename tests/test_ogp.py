from flask_dance.consumer.storage import MemoryStorage
from spotify_wordcloud import app
from spotify_wordcloud.api.auth import spotify_bp


def test_ogp(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(spotify_bp, "storage", storage)

    with app.test_client() as client:
        res = client.get(
            "/share/bfbe015a6d6318dd2b50b3c9918f4cdf", base_url="https://example.com"
        )

    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert '/wordclouds/bfbe015a6d6318dd2b50b3c9918f4cdf.png"' in text
    assert (
        'content="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png"'
        not in text
    )
