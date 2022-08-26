from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template,
    send_file,
    session,
)
from flask_dance.contrib.spotify import spotify
from google.cloud import storage
from wordcloud import WordCloud

import hashlib
import logging
from os import path, getcwd
import random
import uuid

from spotify_wordcloud.app import db
from spotify_wordcloud.models import Pictures

gcs = storage.Client()


app = Blueprint("image", __name__, url_prefix="/")


stopwords = ("THE", "The")
wc_object = WordCloud(
    font_path=path.join(getcwd(), ".fonts/ipaexg.ttf"),
    width=1200,
    height=630,
    colormap="cool",
    stopwords=stopwords,
    regexp=r"\S[\S']+",
)


def text_and_hash_generation(session):
    logging.info("text_and_hash_generation started")

    data = spotify.get("/v1/me/top/artists?limit=50").json()

    artists = []

    for i, item in enumerate(data["items"]):
        for _ in range((50 - i) // 10):
            artists.append(item["name"])

    random.shuffle(artists)
    text = " ".join(artists)
    session["spotify_wordcloud_text"] = text  # save text
    ha = hashlib.md5(text.encode("utf-8")).hexdigest()
    session["spotify_wordcloud_hash"] = ha  # save hash

    logging.info("text_and_hash_generation ended")


def image_generation(text, ha):
    logging.info("image_generation started")

    freq = wc_object.process_text(text)
    # force regularize
    for k, v in freq.items():
        if v >= 6:
            freq[k] = 6
    wc = wc_object.generate_from_frequencies(freq)

    image = wc.to_image()
    image.save(f"/tmp/{ha}.png", format="png", optimize=True)

    logging.info("image_generation ended")


@app.route("/generate")
def generate():
    if spotify.authorized:
        try:
            if "spotify_wordcloud_text" not in session:
                text_and_hash_generation(session)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if path.exists(f"/tmp/{ha}.png"):
                return send_file(f"/tmp/{ha}.png", mimetype="image/png")

            image_generation(text, ha)

            return send_file(f"/tmp/{ha}.png", mimetype="image/png")

        except Exception as e:
            logging.error(str(e))
            return Response(status=400)

    else:
        return Response(status=401)


@app.route("/regenerate")
def regenerate():
    if spotify.authorized:
        try:
            if "spotify_wordcloud_text" not in session:
                text_and_hash_generation(session)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if "gcs_image_link" in session:
                session.pop("gcs_image_link")
            image_generation(text, ha)

            return send_file(f"/tmp/{ha}.png", mimetype="image/png")

        except Exception as e:
            logging.error(str(e))
            return Response(status=400)

    else:
        return Response(status=401)


@app.route("/save", methods=["POST"])
def save():
    if spotify.authorized:
        try:
            if "spotify_wordcloud_text" not in session:
                text_and_hash_generation(session)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                image_generation(text, ha)

            gcs_filename = str(uuid.uuid4())
            bucket = gcs.get_bucket(current_app.config["CLOUD_STORAGE_BUCKET"])
            blob = bucket.blob(f"wordclouds/{gcs_filename}.png")
            blob.upload_from_filename(f"/tmp/{ha}.png")

            # save to DB
            record = Pictures(
                user_id=session["user_id"], file_name=f"{gcs_filename}.png"
            )
            db.session.add(record)
            db.session.commit()

            return render_template("result.html", result="画像の保存に成功しました。")

        except Exception as e:
            logging.error(str(e))
            return render_template("result.html", result="画像の保存に失敗しました。"), 500

    else:
        return Response(status=401)


@app.route("/shareLink")
def link():
    if spotify.authorized:
        try:
            if "spotify_wordcloud_text" not in session:
                text_and_hash_generation(session)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                image_generation(text, ha)

            if "gcs_image_link" not in session:
                gcs_filename = str(uuid.uuid4())
                bucket = gcs.get_bucket(current_app.config["CLOUD_STORAGE_BUCKET"])
                blob = bucket.blob(f"wordclouds/{gcs_filename}.png")
                blob.upload_from_filename(f"/tmp/{ha}.png")
                image_link = f"https://spotify-word.cloud/share/{gcs_filename}"
                session["gcs_image_link"] = image_link

            return jsonify({"link": session["gcs_image_link"]})

        except Exception as e:
            logging.error(str(e))
            return render_template("result.html", result="画像付きリンクの取得に失敗しました。"), 500
    else:
        return Response(status=401)


@app.route("/shareTwitter", methods=["POST"])
def tweet():
    if spotify.authorized:
        try:
            if "spotify_wordcloud_text" not in session:
                text_and_hash_generation(session)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                image_generation(text, ha)

            gcs_filename = str(uuid.uuid4())
            bucket = gcs.get_bucket(current_app.config["CLOUD_STORAGE_BUCKET"])
            blob = bucket.blob(f"wordclouds/{gcs_filename}.png")
            blob.upload_from_filename(f"/tmp/{ha}.png")

            message = f"%0D%0ASpotify+WordCloud+でワードクラウドを作りました！%0D%0A%23Spotify_WordCloud%0D%0Ahttps://spotify-word.cloud/share/{gcs_filename}"
            return redirect(f"https://twitter.com/intent/tweet?text={message}")

        except Exception as e:
            logging.error(str(e))
            return render_template("result.html", result="ツイートに失敗しました。"), 500
    else:
        return Response(status=401)
