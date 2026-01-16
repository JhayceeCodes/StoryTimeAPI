from rest_framework.throttling import UserRateThrottle , AnonRateThrottle   


class StoryAnonThrottle(AnonRateThrottle):
    scope = "story_anon"

class StoryUserThrottle(UserRateThrottle):
    scope = "story_user"

class StoryCreateThrottle(UserRateThrottle):
    scope = "story_create"

class StoryDeleteThrottle(UserRateThrottle):
    scope = "story_delete"

class ReactionBurstThrottle(UserRateThrottle):
    scope = "reaction_burst"

class ReactionSustainedThrottle(UserRateThrottle):
    scope = "reaction_sustained"

class RatingBurstThrottle(UserRateThrottle):
    scope = "rating_burst"

class RatingSustainedThrottle(UserRateThrottle):
    scope = "rating_sustained"

class ReviewCreateThrottle(UserRateThrottle):
    scope = "review_create"

class ReviewDeleteThrottle(UserRateThrottle):
    scope = "review_delete"