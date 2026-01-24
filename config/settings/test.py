# config/settings/test.py
from .base import *

DEBUG = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,

    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],

    "DEFAULT_THROTTLE_CLASSES": [
     'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        # Global
        "user": "500/hour",
        "anon": "100/hour",

        # Stories
        "story_anon": "50/min",
        "story_user": "300/hour",
        "story_create": "100/hour",

        # Reactions
        "reaction_burst": "10/min",
        "reaction_sustained": "50/hour",

        # Ratings
        "rating_burst": "20/min",
        "rating_sustained": "10/hour",

        # Reviews
        "review_create": "20/hour",
        "review_delete": "50/hour",

        # Moderation
        "story_delete": "20/hour",

        # Auth
        "login": "50/min",
        "password_reset": "500/hour",
        "email_verify": "50/hour",
    },

    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler"
}