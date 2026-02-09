from .base import *


DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

PERFORMANCE_TESTING_MODE = os.getenv("PERFORMANCE_TESTING_MODE", "false").lower() == "true"

if PERFORMANCE_TESTING_MODE:
    print("PERFORMANCE TESTING MODE ENABLED...")



    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
        # Global
        "anon": "100000/min",
        "user": "100000/min",

        # Stories
        "story_anon": "100000/min",
        "story_user": "100000/min",
        "story_create": "100000/min",
        "story_delete": "100000/min",

        # Reactions
        "reaction_burst": "100000/min",
        "reaction_sustained": "100000/min",

        # Ratings
        "rating_burst": "100000/min",
        "rating_sustained": "100000/min",

        # Reviews
        "review_create": "100000/min",
        "review_delete": "100000/min",

        # Auth
        "login": "100000/min",
        "password_reset": "100000/min",
        "email_verify": "100000/min",
    }
