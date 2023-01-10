from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)
import flask_dance.consumer
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify


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
        return render_template("authorized.html")
    else:
        return render_template("unauthorized.html")


@app.route("/login")
def login():
    return redirect(url_for("spotify.login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
