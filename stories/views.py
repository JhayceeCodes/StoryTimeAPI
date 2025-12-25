from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render
from .serializers import StorySerializer, StoryReactionSerializer
from .models import Story
from .permissions import IsAuthor, IsStoryOwner, CanDeleteStory

""""
All users, authenticated or not, can read stories

Only authors can create story 

Any update can only be done by story author

Delete can be done by the story author, moderator, or admin
"""

class StoryViewSet(ModelViewSet):
    queryset =Story.objects.all().select_related("author").order_by("-created_at")
    serializer_class = StorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action == "create":
            return [IsAuthor()]

        if self.action in ["update", "partial_update"]:
            return [IsStoryOwner()]

        if self.action == "destroy":
            return [CanDeleteStory()]

        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user.author)
    
