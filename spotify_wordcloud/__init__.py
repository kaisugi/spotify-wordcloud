from spotify_wordcloud.app import app
from spotify_wordcloud.api import auth, image, history, ogp, misc

app.register_blueprint(auth.spotify_bp, url_prefix="/login")
app.register_blueprint(auth.app)
app.register_blueprint(image.app)
app.register_blueprint(history.app)
app.register_blueprint(ogp.app)
app.register_blueprint(misc.app)
