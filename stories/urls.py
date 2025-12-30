from rest_framework import routers
from django.urls import path
from .views import StoryViewSet, ReactionView


router = routers.DefaultRouter()

router.register("stories", StoryViewSet, basename="story")


urlpatterns = [
    path("stories/<int:story_id>/reaction/", ReactionView.as_view(), name="story-reaction"),
]
urlpatterns += router.urls


