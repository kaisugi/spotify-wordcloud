from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


def page_not_found(_):
    return render_template("404.html"), 404


app = Flask(__name__)
app.register_error_handler(404, page_not_found)
app.config.from_object("spotify_wordcloud.config")

csrf = CSRFProtect(app)

if not app.config["FLASK_DEBUG"]:
    talisman = Talisman(
        app,
        content_security_policy="default-src https: self; "
        "script-src https: 'unsafe-inline'; "
        "style-src https: 'unsafe-inline'; "
        "img-src * blob:;",
    )

    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()

db = SQLAlchemy(app)
