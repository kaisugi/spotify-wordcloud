from flask import Flask
from flask_dance.contrib.spotify import make_spotify_blueprint
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