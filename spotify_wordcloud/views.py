from flask import *
from flask_dance.contrib.spotify import spotify
from wordcloud import WordCloud
import tweepy
import boto3

from os import path
from datetime import date, datetime
import logging
import hashlib

from spotify_wordcloud import app, db
from .models import Pictures

s3_client = boto3.client('s3', region_name='ap-northeast-1')



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
    auth = tweepy.OAuthHandler(app.config["TWITTER_API_KEY"], app.config["TWITTER_API_SECRET"], 'https://spotify-wordcloud.herokuapp.com/callback')

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


@app.route('/regenerate')
def regenerate():
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

            wc = WordCloud(font_path='/app/.fonts/ipaexg.ttf', width=1024, height=576, colormap='cool', stopwords=set()).generate(text)
            image = wc.to_image()
            image.save(f"/tmp/{ha}.png", format='png', optimize=True)

            return send_file(f"/tmp/{ha}.png", mimetype='image/png')

        except Exception as e:
            logging.error(str(e))
            return Response(status=400)

    else:
        return Response(status=401)


@app.route('/save', methods=['POST'])
def save():
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

            # set filename from timestamp
            t_today = datetime.now()
            s_today = t_today.strftime('%Y/%m/%d %H:%M*%S')
            s3_filename = hashlib.md5(s_today.encode('utf-8')).hexdigest()

            s3_client.upload_file(f"/tmp/{ha}.png", "spotify-wordcloud", f"{s3_filename}.png", ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'})


            # save to DB
            profile = spotify.get("v1/me").json()
            record = Pictures(user_id=profile["id"], file_name=f"{s3_filename}.png")
            db.session.add(record)
            db.session.commit()

            return render_template('result.html', result="画像の保存に成功しました。")


        except Exception as e:
            logging.error(str(e))
            return render_template('result.html', result="画像の保存に失敗しました。")

    else:
        return Response(status=401)    


@app.route('/tweet', methods=['POST'])
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
            auth = tweepy.OAuthHandler(app.config["TWITTER_API_KEY"], app.config["TWITTER_API_SECRET"], 'https://spotify-wordcloud.herokuapp.com/callback')
            token = session.pop('request_token', None)
            auth.request_token = token
            verifier = session.pop('oauth_verifier', None)
            auth.get_access_token(verifier)

            api = tweepy.API(auth)

            filename = f"/tmp/{ha}.png"
            res = api.media_upload(filename)
            api.update_status("Spotifyで自己紹介！\n#Spotify_WordCloud\nhttps://spotify-wordcloud.herokuapp.com/", media_ids=[res.media_id])
            
            return render_template('result.html', result="ツイートに成功しました。")

        except Exception as e:
            logging.error(str(e))
            return render_template('result.html', result="ツイートに失敗しました。")
    else:
        return Response(status=401)


@app.route('/history')
def history():
    if spotify.authorized:
        profile = spotify.get("v1/me").json()
        pictures = db.session.query(Pictures).filter(Pictures.user_id==profile["id"]).order_by(Pictures.created_at.desc()).all()
        db.session.commit()

        return render_template('history.html', pictures=pictures)

    else:
        return Response(status=401)


@app.route('/history/<string:file_hash>', methods=['POST'])
def delete_picture(file_hash):
    if spotify.authorized:
        if request.form.get('_method') == 'DELETE':
            profile = spotify.get("v1/me").json()
            pictures = db.session.query(Pictures).filter(Pictures.file_name==(file_hash+".png"))\
                .filter(Pictures.user_id==profile["id"]).delete()
            db.session.commit()

            return redirect("/history")

    else:
        return Response(status=401)