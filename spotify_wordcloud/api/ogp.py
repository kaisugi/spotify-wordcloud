from flask import Blueprint, current_app, render_template


app = Blueprint("ogp", __name__, url_prefix="/")


@app.route("/share/<string:file_hash>")
def share(file_hash):
    return render_template(
        "ogp.html",
        file_name=file_hash,
        cloud_storage_bucket=current_app.config["CLOUD_STORAGE_BUCKET"],
    )
