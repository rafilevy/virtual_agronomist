from .base import *  # noqa


DEBUG = False
STATICFILES_DIRS = (base_dir_join("js-build"),)
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "secret"

STATIC_ROOT = base_dir_join("staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = base_dir_join("mediafiles")
MEDIA_URL = "/media/"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Logging
MIDDLEWARE.insert(  # insert RequestIDMiddleware on the top
    0, "log_request_id.middleware.RequestIDMiddleware"
)

LOG_REQUESTS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s"}, },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard", },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG"},
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        "log_request_id.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": True,  # on DEBUG should be False
        "STATS_FILE": base_dir_join("./webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+\.hot-update.js", ".+\.map"],
        'LOADER_CLASS': 'chatapp.webpack.CustomWebpackLoader',
    }
}

JS_REVERSE_EXCLUDE_NAMESPACES = ["admin"]
