from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render
from .serializers import StorySerializer, StoryReactionSerializer
from .models import Story


""""
All users, authenticated or not, can read stories

Only authors can create story 

Any update can only be done by story author

Delete can be done by the story author, moderator, or admin
"""

class StoryViewSet(ModelViewSet):
    queryset =Story.objects.all().select_related("author").order_by("-created_at")
    serializer_class = StorySerializer

    
