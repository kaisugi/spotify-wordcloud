from dotenv import load_dotenv

from os import environ, path
from pathlib import Path

load_dotenv(verbose=True)

parent_path = Path(__file__).parent
dotenv_path = path.join(parent_path, ".env")
load_dotenv(dotenv_path)

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SECRET_KEY = environ.get("SECRET_KEY")

SPOTIFY_OAUTH_CLIENT_ID = environ.get("SPOTIFY_OAUTH_CLIENT_ID")
SPOTIFY_OAUTH_CLIENT_SECRET = environ.get("SPOTIFY_OAUTH_CLIENT_SECRET")

CLOUD_STORAGE_BUCKET = environ.get("CLOUD_STORAGE_BUCKET")

FLASK_DEBUG = environ.get("FLASK_DEBUG")
TESTING = environ.get("TESTING")

if FLASK_DEBUG or TESTING:
    CALLBACK_URL = environ.get("CALLBACK_URL_DEV")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL_DEV")
else:
    CALLBACK_URL = environ.get("CALLBACK_URL")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

SQLALCHEMY_TRACK_MODIFICATIONS = True
# https://qiita.com/cress_cc/items/7e68e535b405e1bb50a1
# https://stackoverflow.com/questions/58866560/flask-sqlalchemy-pool-pre-ping-only-working-sometimes
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
