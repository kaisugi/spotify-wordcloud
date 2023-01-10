from flask import Blueprint

import logging

from spotify_wordcloud.models import Pictures

app = Blueprint("misc", __name__, url_prefix="/")


# https://cloud.google.com/appengine/docs/standard/python3/configuring-warmup-requests
@app.route("/_ah/warmup")
def warmup():
    return "", 200, {}


# DB healthcheck
@app.route("/dbcheck")
def dbcheck():
    count = Pictures.query.count()
    logging.info(f"total number of pictures: {count}")
    return "", 200, {}
