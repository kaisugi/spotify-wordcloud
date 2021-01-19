from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    Response,
    session
)
from flask_dance.contrib.spotify import spotify

import logging

from spotify_wordcloud.app import db
from spotify_wordcloud.models import Pictures

app = Blueprint("history", __name__, url_prefix="/")


@app.route("/history")
def history():
    if spotify.authorized:
        try:
            pictures = (
                db.session.query(Pictures)
                .filter(Pictures.user_id == session["user_id"])
                .order_by(Pictures.created_at.desc())
                .all()
            )
            db.session.commit()

            return render_template("history.html", pictures=pictures,
                                   aws_s3_url=current_app.config["AWS_S3_URL"])

        except Exception as e:
            logging.error(str(e))
            return render_template(
                "result.html", result="画像一覧の表示に失敗しました。時間を置いて再度試してみてください。"
            )

    else:
        return Response(status=401)


@app.route("/history/<string:file_hash>", methods=["POST"])
def delete_picture(file_hash):
    if spotify.authorized and (request.form.get("_method") == "DELETE"):
        try:
            db.session.query(Pictures)\
                .filter(Pictures.file_name == (file_hash + ".png"))\
                .filter(Pictures.user_id == session["user_id"])\
                .delete()
            db.session.commit()

            return redirect("/history")

        except Exception as e:
            logging.error(str(e))
            return render_template(
                "result.html", result="画像の削除に失敗しました。時間を置いて再度試してみてください。"
            )

    else:
        return Response(status=401)
