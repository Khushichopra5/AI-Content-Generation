from .base import *  # noqa: F403

SECRET_KEY = "test-secret-key"
DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",
    }
}
STATIC_ROOT = BASE_DIR / "test-staticfiles"
MEDIA_ROOT = BASE_DIR / "test-media"
STATIC_ROOT.mkdir(exist_ok=True)
MEDIA_ROOT.mkdir(exist_ok=True)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
OPENAI_API_KEY = "test-openai-key"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "contentgen-tests",
    }
}
