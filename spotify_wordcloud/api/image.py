import boto3
from flask import Blueprint, Response, current_app, render_template, send_file, session
from flask_dance.contrib.spotify import spotify
import tweepy
from wordcloud import WordCloud

from datetime import datetime
import hashlib
import logging
from os import path

from spotify_wordcloud.app import db
from spotify_wordcloud.models import Pictures

s3_client = boto3.client("s3", region_name="ap-northeast-1")


app = Blueprint("image", __name__, url_prefix="/")


def hash_generation(session, text):
    data = spotify.get("/v1/me/top/artists?limit=50").json()

    for i, item in enumerate(data["items"]):
        for k in range((50 - i) // 10):
            text += item["name"]
            text += " "

    session["spotify_wordcloud_text"] = text  # save text
    ha = hashlib.md5(text.encode("utf-8")).hexdigest()
    session["spotify_wordcloud_hash"] = ha  # save hash

    return text


def image_generation(text, ha):
    stopwords = ("THE", "The")

    freq = WordCloud(stopwords=stopwords).process_text(text)
    # force regularize
    for k, v in freq.items():
        if v >= 6:
            freq[k] = 6
    wc = WordCloud(
        font_path="/app/.fonts/ipaexg.ttf",
        width=1024,
        height=576,
        colormap="cool",
        stopwords=stopwords,
    ).generate_from_frequencies(freq)
    image = wc.to_image()
    image.save(f"/tmp/{ha}.png", format="png", optimize=True)


@app.route("/generate")
def generate():
    if spotify.authorized:
        try:
            text = ""

            if "spotify_wordcloud_text" not in session:
                text = hash_generation(session, text)

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
            text = ""

            if "spotify_wordcloud_text" not in session:
                text = hash_generation(session, text)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

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
            text = ""

            if "spotify_wordcloud_text" not in session:
                text = hash_generation(session, text)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                image_generation(text, ha)

            # set filename from timestamp
            t_today = datetime.now()
            s_today = t_today.strftime("%Y/%m/%d %H:%M*%S")
            s3_filename = hashlib.md5(s_today.encode("utf-8")).hexdigest()

            s3_client.upload_file(
                f"/tmp/{ha}.png",
                "spotify-wordcloud",
                f"{s3_filename}.png",
                ExtraArgs={"ACL": "public-read", "ContentType": "image/png"},
            )

            # save to DB
            record = Pictures(
                user_id=session["user_id"], file_name=f"{s3_filename}.png"
            )
            db.session.add(record)
            db.session.commit()

            return render_template("result.html", result="画像の保存に成功しました。")

        except Exception as e:
            logging.error(str(e))
            return render_template("result.html", result="画像の保存に失敗しました。")

    else:
        return Response(status=401)


@app.route("/tweet", methods=["POST"])
def tweet():
    if spotify.authorized:
        try:
            text = ""

            if "spotify_wordcloud_text" not in session:
                text = hash_generation(session, text)

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                image_generation(text, ha)

            # Upload Media to Twitter
            auth = tweepy.OAuthHandler(
                current_app.config["TWITTER_API_KEY"],
                current_app.config["TWITTER_API_SECRET"],
                current_app.config["CALLBACK_URL"],
            )
            token = session.pop("request_token", None)
            auth.request_token = token
            verifier = session.pop("oauth_verifier", None)
            auth.get_access_token(verifier)

            api = tweepy.API(auth)

            filename = f"/tmp/{ha}.png"
            res = api.media_upload(filename)
            api.update_status(
                "Spotifyで自己紹介！\n#Spotify_WordCloud\n"
                + "https://spotify-wordcloud.herokuapp.com/",
                media_ids=[res.media_id],
            )

            return render_template("result.html", result="ツイートに成功しました。")

        except Exception as e:
            logging.error(str(e))
            return render_template("result.html", result="ツイートに失敗しました。")
    else:
        return Response(status=401)
