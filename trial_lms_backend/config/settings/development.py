from .base import *

DEBUG = True

ALLOWED_HOSTS = [
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 6-6)
    "localhost",
    "127.0.0.1",
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 8-8)
]

##Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = True

SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

SECURE_HSTS_INCLUDE_SUBDOMAINS = False

SECURE_HSTS_PRELOAD = False

