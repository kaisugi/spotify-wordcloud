from flask import Flask, session
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
import flask_dance.consumer
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('spotify_wordcloud.config')

csrf = SeaSurf(app)

talisman = Talisman(
    app,
    content_security_policy="default-src https: self; script-src https: 'unsafe-inline'; style-src https: 'unsafe-inline'; img-src * blob:;"
)
db = SQLAlchemy(app)

import spotify_wordcloud.views

spotify_bp = make_spotify_blueprint(scope="user-top-read")
app.register_blueprint(spotify_bp, url_prefix="/login")


@flask_dance.consumer.oauth_authorized.connect_via(spotify_bp)
def spotify_logged_in(blueprint, token):
    session.clear()

    profile = spotify.get("v1/me").json()
    session['user_id'] = profile["id"]
    