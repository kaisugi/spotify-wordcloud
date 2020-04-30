from flask import *
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from wordcloud import WordCloud
import tweepy

from os import environ, path
import logging
import hashlib


app = Flask(__name__)
csrf = SeaSurf(app)

talisman = Talisman(
    app,
    content_security_policy="default-src https: self; script-src https: 'unsafe-inline'; style-src https: 'unsafe-inline'"
)

app.secret_key = environ.get("SECRET_KEY")
app.config["SPOTIFY_OAUTH_CLIENT_ID"] = environ.get("SPOTIFY_OAUTH_CLIENT_ID")
app.config["SPOTIFY_OAUTH_CLIENT_SECRET"] = environ.get("SPOTIFY_OAUTH_CLIENT_SECRET")
spotify_bp = make_spotify_blueprint(scope="user-top-read")
app.register_blueprint(spotify_bp, url_prefix="/login")



@app.route("/")
def index():
    if spotify.authorized:
        if 'oauth_verifier' in session:
            return render_template('authorized.html', twitter_authorized=True)
        else:
            return render_template('authorized.html', twitter_authorized=False)
    else:
        return render_template('unauthorized.html')


@app.route("/login")
def login():
    return redirect(url_for("spotify.login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/twitter_auth')
def twitter_auth():
    redirect_url = ""
    auth = tweepy.OAuthHandler(environ.get("TWITTER_API_KEY"), environ.get("TWITTER_API_SECRET"), 'http://localhost:5000/callback')

    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
    except tweepy.TweepError as e:
        logging.error(str(e))

    return redirect(redirect_url)


@app.route("/callback")
def callback():
    session['oauth_verifier'] = request.args.get('oauth_verifier')
    return redirect("/")


@app.route('/generate')
def generate():
    if spotify.authorized:
        try:
            text = ""

            if "spotify_wordcloud_text" not in session:
                data = spotify.get("/v1/me/top/artists?limit=50").json()

                for i, item in enumerate(data['items']):
                    for k in range((50-i)//10):
                        text += item['name']
                        text += " "

                session["spotify_wordcloud_text"] = text  # save text
                ha = hashlib.md5(text.encode('utf-8')).hexdigest()
                session["spotify_wordcloud_hash"] = ha  # save hash

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if path.exists(f"/tmp/{ha}.png"):
                return send_file(f"/tmp/{ha}.png", mimetype='image/png')

            wc = WordCloud(font_path='/app/.fonts/ipaexg.ttf', width=1024, height=576, colormap='cool', stopwords=set()).generate(text)
            image = wc.to_image()
            image.save(f"/tmp/{ha}.png", format='png', optimize=True)

            return send_file(f"/tmp/{ha}.png", mimetype='image/png')

        except Exception as e:
            logging.error(str(e))
            return Response(status=400)

    else:
        return Response(status=401)


@app.route('/tweet')
def tweet():
    if spotify.authorized:
        try:
            text = ""

            if "spotify_wordcloud_text" not in session:
                data = spotify.get("/v1/me/top/artists?limit=50").json()

                for i, item in enumerate(data['items']):
                    for k in range((50-i)//10):
                        text += item['name']
                        text += " "

                session["spotify_wordcloud_text"] = text  # save text
                ha = hashlib.md5(text.encode('utf-8')).hexdigest()
                session["spotify_wordcloud_hash"] = ha  # save hash

            text = session["spotify_wordcloud_text"]
            ha = session["spotify_wordcloud_hash"]

            if not path.exists(f"/tmp/{ha}.png"):
                wc = WordCloud(font_path='/app/.fonts/ipaexg.ttf', width=1024, height=576, colormap='cool', stopwords=set()).generate(text)
                image = wc.to_image()
                image.save(f"/tmp/{ha}.png", format='png', optimize=True)

            # Upload Media to Twitter
            auth = tweepy.OAuthHandler(environ.get("TWITTER_API_KEY"), environ.get("TWITTER_API_SECRET"), 'http://localhost:5000/callback')
            token = session.pop('request_token', None)
            auth.request_token = token
            verifier = session.pop('oauth_verifier', None)
            auth.get_access_token(verifier)

            api = tweepy.API(auth)

            filename = f"/tmp/{ha}.png"
            res = api.media_upload(filename)
            api.update_status("Spotifyで自己紹介！\n#Spotify_Wordcloud\nhttps://spotify-wordcloud.herokuapp.com/", media_ids=[res.media_id])
            
            return render_template('tweet_success.html')

        except Exception as e:
            logging.error(str(e))
            return render_template('tweet_failure.html')
    else:
        return Response(status=401)


if __name__ == '__main__':
    app.run()