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

TWITTER_API_KEY = environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = environ.get("TWITTER_API_SECRET")

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_URL = environ.get("AWS_S3_URL")

SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = True

FLASK_DEBUG = environ.get("FLASK_DEBUG")
