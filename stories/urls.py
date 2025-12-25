from rest_framework import routers
from .views import StoryViewSet


router = routers.DefaultRouter()

router.register("stories", StoryViewSet, basename="story")

urlpatterns = router.urls
