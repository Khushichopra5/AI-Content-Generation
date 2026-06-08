from __future__ import annotations

from pathlib import Path

import dj_database_url

from apps.common.env import env

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = env.str("DJANGO_SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = env.bool("DJANGO_DEBUG", env.bool("DEBUG", False))
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"]),
)
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", DEBUG)
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    ["http://localhost:3000", "http://127.0.0.1:3000"],
)
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-Guest-Id",
    "X-Session-Id",
    "X-Device-Id",
    "X-Request-ID",
]
CORS_PREFLIGHT_MAX_AGE_SECONDS = env.int("CORS_PREFLIGHT_MAX_AGE_SECONDS", 86400)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.authentication",
    "apps.brands",
    "apps.guests",
    "apps.templates",
    "apps.generation",
    "apps.usage",
    "apps.common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.common.middleware.CORSMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.RequestIDMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        env.str(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/contentgen",
        ),
        conn_max_age=env.int("DB_CONN_MAX_AGE", 60),
    )
}

AUTH_USER_MODEL = "authentication.User"

LANGUAGE_CODE = "en-us"
TIME_ZONE = env.str("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = env.str("REDIS_URL", "redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "contentgen",
        "TIMEOUT": env.int("CACHE_TIMEOUT_SECONDS", 3600),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "apps.authentication.authentication.BearerTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.common.throttling.UserBurstRateThrottle",
        "apps.common.throttling.UserSustainedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user_burst": env.str("API_THROTTLE_USER_BURST", "30/min"),
        "user_sustained": env.str("API_THROTTLE_USER_SUSTAINED", "500/day"),
        "anon": env.str("API_THROTTLE_ANON", "10/min"),
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = env.bool("CELERY_TASK_EAGER_PROPAGATES", False)
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_TASK_DEFAULT_QUEUE = "default"

OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")
OPENAI_TEXT_MODEL = env.str("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
OPENAI_IMAGE_MODEL = env.str("OPENAI_IMAGE_MODEL", "gpt-image-1")
OPENAI_REQUEST_TIMEOUT = env.int("OPENAI_REQUEST_TIMEOUT", 90)
OPENAI_IMAGE_REQUEST_TIMEOUT = env.int("OPENAI_IMAGE_REQUEST_TIMEOUT", max(OPENAI_REQUEST_TIMEOUT, 180))

CONTENT_CACHE_TTL_SECONDS = env.int("CONTENT_CACHE_TTL_SECONDS", 3600)
JOB_STATUS_CACHE_TTL_SECONDS = env.int("JOB_STATUS_CACHE_TTL_SECONDS", 300)
DEDUP_LOCK_TTL_SECONDS = env.int("DEDUP_LOCK_TTL_SECONDS", 180)
GUEST_SESSION_TTL_SECONDS = env.int("GUEST_SESSION_TTL_SECONDS", 60 * 60 * 24 * 14)
GUEST_RETENTION_DAYS = env.int("GUEST_RETENTION_DAYS", 14)
GUEST_DAILY_GENERATION_SOFT_LIMIT = env.int("GUEST_DAILY_GENERATION_SOFT_LIMIT", 25)
GUEST_DAILY_BRAND_SOFT_LIMIT = env.int("GUEST_DAILY_BRAND_SOFT_LIMIT", 10)
GUEST_DAILY_TEMPLATE_SOFT_LIMIT = env.int("GUEST_DAILY_TEMPLATE_SOFT_LIMIT", 10)
GUEST_REDIS_KEY_PREFIX = env.str("GUEST_REDIS_KEY_PREFIX", "guest-session")

OBJECT_STORAGE_BACKEND = env.str("OBJECT_STORAGE_BACKEND", "local")
OBJECT_STORAGE_MEDIA_PREFIX = env.str("OBJECT_STORAGE_MEDIA_PREFIX", "generated")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {"handlers": ["console"], "level": env.str("LOG_LEVEL", "INFO")},
}
