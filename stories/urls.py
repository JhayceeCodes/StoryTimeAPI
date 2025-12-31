from rest_framework_nested import routers
from django.urls import path
from .views import StoryViewSet, ReactionView, ReviewViewSet


router = routers.DefaultRouter()

router.register("stories", StoryViewSet, basename="stories")

stories_router = routers.NestedDefaultRouter(router, "stories", lookup="story")
stories_router.register("reviews", ReviewViewSet, basename="story-reviews")


urlpatterns = router.urls + stories_router.urls + [
    path("stories/<int:story_id>/reaction/", ReactionView.as_view(), name="story-reaction"),
]



