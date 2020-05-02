from os import environ, path

CSRF_COOKIE_SECURE = True
CSRT_COOKIE_HTTPONLY = True

SECRET_KEY = environ.get("SECRET_KEY")
SPOTIFY_OAUTH_CLIENT_ID = environ.get("SPOTIFY_OAUTH_CLIENT_ID")
SPOTIFY_OAUTH_CLIENT_SECRET = environ.get("SPOTIFY_OAUTH_CLIENT_SECRET")
