from flask import *
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from wordcloud import WordCloud
import requests

from os import environ, path
import hashlib


app = Flask(__name__)
app.secret_key = environ.get("SECRET_KEY")

app.config["SPOTIFY_OAUTH_CLIENT_ID"] = environ.get("SPOTIFY_OAUTH_CLIENT_ID")
app.config["SPOTIFY_OAUTH_CLIENT_SECRET"] = environ.get("GITHUB_OAUTH_CLIENT_SECRET")
spotify_bp = make_spotify_blueprint(scope="user-top-read")
app.register_blueprint(spotify_bp, url_prefix="/login")

app.config["TWITTER_OAUTH_CLIENT_KEY"] = environ.get("TWITTER_OAUTH_CLIENT_KEY")
app.config["TWITTER_OAUTH_CLIENT_SECRET"] = environ.get("TWITTER_OAUTH_CLIENT_SECRET")
twitter_bp = make_twitter_blueprint()
app.register_blueprint(twitter_bp, url_prefix="/login")



@app.route("/")
def index():
    if spotify.authorized:
        if twitter.authorized:
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


@app.route("/twitter_login")
def twitter_login():
    return redirect(url_for("twitter.login"))


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
            print(e)
            return Response(status=400)

    else:
        return Response(status=401)


@app.route('/tweet')
def tweet():
    if twitter.authorized:
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


                res = twitter.post("https://api.twitter.com/1.1/statuses/update.json?status=Gyazoで画像付きツイートにしようかな。").json()
                print(res)

                
                return "Tweet success"

            except Exception as e:
                print(e)
                return Response(status=400)
        else:
            return Response(status=401)

    else:
        return redirect(url_for("twitter.login"))


if __name__ == '__main__':
    app.run()