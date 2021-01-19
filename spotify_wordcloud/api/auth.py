from flask import *
import flask_dance.consumer
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
import tweepy

import logging

spotify_bp = make_spotify_blueprint(scope="user-top-read")


@flask_dance.consumer.oauth_authorized.connect_via(spotify_bp)
def spotify_logged_in(blueprint, token):
    session.clear()

    profile = spotify.get("v1/me").json()
    session["user_id"] = profile["id"]


app = Blueprint("auth", __name__, url_prefix="/")


@app.route("/")
def index():
    if spotify.authorized:
        if "oauth_verifier" in session:
            return render_template("authorized.html", twitter_authorized=True)
        else:
            return render_template("authorized.html", twitter_authorized=False)
    else:
        return render_template("unauthorized.html")


@app.route("/login")
def login():
    return redirect(url_for("spotify.login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/twitter_auth")
def twitter_auth():
    redirect_url = ""
    auth = tweepy.OAuthHandler(
        current_app.config["TWITTER_API_KEY"],
        current_app.config["TWITTER_API_SECRET"],
        "https://spotify-wordcloud.herokuapp.com/callback",
    )

    try:
        redirect_url = auth.get_authorization_url()
        session["request_token"] = auth.request_token
    except tweepy.TweepError as e:
        logging.error(str(e))

    return redirect(redirect_url)


@app.route("/callback")
def callback():
    try:
        session["oauth_verifier"] = request.args.get("oauth_verifier")
        return redirect("/")

    except Exception as e:
        logging.error(str(e))
        return Response(status=500)
