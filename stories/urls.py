from rest_framework import routers
from django.urls import path
from .views import StoryViewSet, StoryReactionView


router = routers.DefaultRouter()

router.register("stories", StoryViewSet, basename="story")


urlpatterns = [
    path("stories/<int:story_id>/reaction/", StoryReactionView.as_view(), name="story-reaction"),
]
urlpatterns += router.urls


