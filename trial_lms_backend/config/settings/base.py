from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

DEBUG = config(
    "DEBUG",
    cast=bool,
    default=False
)

ALLOWED_HOSTS = [
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 17-17)
    "localhost",
    "*",
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third part libs
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',

    #JWT
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    #Created Apps
    'users',
    'schools',
    'academics',
    'content_management',
    'assessment_management',
    'homework_management',
    'analytics_performance',
    'audit_logs',
    'notifications',
]

## Common Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = "users.User"

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

##Security Settings

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"

## JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME_MINUTES", cast=int, default=60)
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME_DAYS", cast=int, default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,

    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": True,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "ALGORITHM": "HS256",
}

##REST Configurations
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/min",
        "user": "500/hour",
        "login": "10/min",
        "register": "5/min",
    },

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    )
}


## Logging Configuration

LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format":
            "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },

    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/application.log",
            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": ["file"],
        "level": "INFO",
    },
}

# --------------------------------------------------
# REDIS CACHE
# --------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6380/1",
        "OPTIONS": {
            "CLIENT_CLASS":
                "django_redis.client.DefaultClient",
        },
    }
}


# --------------------------------------------------
# CELERY
# --------------------------------------------------

CELERY_BROKER_URL = (
    "redis://127.0.0.1:6380/0"
)

CELERY_RESULT_BACKEND = (
    "redis://127.0.0.1:6380/0"
)

CELERY_ACCEPT_CONTENT = [
    "json"
]

CELERY_TASK_SERIALIZER = (
    "json"
)

CELERY_RESULT_SERIALIZER = (
    "json"
)

CELERY_TIMEZONE = (
    "UTC"
)

# =====================================================
# Queue Routing
# =====================================================

CELERY_TASK_ROUTES = {

    "assessment_management.tasks.*": {
        "queue": "assessment"
    },

    "analytics_performance.tasks.*": {
        "queue": "analytics"
    },

    "content_management.tasks.*": {
        "queue": "content"
    },

    "homework_management.tasks.*": {
        "queue": "homework"
    },

    "notifications.tasks.*": {
        "queue": "notifications"
    },
}

# ==================================================
# Celery BEAT Schedule
# ==================================================

from celery.schedules import crontab


CELERY_BEAT_SCHEDULE = {

    "homework-reminders": {

        "task":
            "notifications.tasks.queue_homework_reminders",

        "schedule":
            crontab(
                minute=0,
                hour="*/6"
            ),
    },
}