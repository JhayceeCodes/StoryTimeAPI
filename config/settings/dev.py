from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True


if DEBUG:
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update({
        "anon": "10000/min",
        "user": "10000/min",

        "story_anon": "10000/min",
        "story_user": "10000/hour",
    })
