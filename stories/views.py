from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from django.db import transaction
from django.shortcuts import get_object_or_404
from .serializers import StorySerializer, StoryReactionSerializer
from .models import Story, StoryReaction
from .permissions import IsAuthor, IsStoryOwner, CanDeleteStory

""""
- All users, authenticated or not, can read stories
- Only authors can create story 
- Any update can only be done by story author
- Delete can be done by the story author, moderator, or admin
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
    

"""
- user reacts to a story by sending a POST with story_id and reaction (like or dislike)
- user can also send a DELETE to cancel the reaction
 -- if user has already reacted before using the same reaction type e.g. if a user tries to like a post twice, it will be rejected
 -- however if the second-time reaction is different from the initial reaction, the previous is cancelled and its counter is reduced 
"""

class StoryReactionView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, story_id):

        story = get_object_or_404(Story, id=story_id)

        serializer = StoryReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction_type = serializer.validated_data["reaction"]

        reaction, created = StoryReaction.objects.get_or_create(
            user=request.user,
            story=story,
            defaults={"reaction": reaction_type}
        )

        if not created:
            return Response(
                {"detail": "Reaction already exists. Use PATCH to update."},
                status=status.HTTP_409_CONFLICT
            )
        
        if reaction_type == "like":
            Story.objects.filter(id=story.id).update(likes=F("likes") + 1)
        else:
            Story.objects.filter(id=story.id).update(dislikes=F("dislikes") + 1)

        reaction.reaction = reaction_type
        reaction.save(update_fields=["reaction"])

        return Response(
            {"message": "Reaction added"},
            status=status.HTTP_201_CREATED
        )
    
        
    @transaction.atomic
    def patch(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        serializer = StoryReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_reaction = serializer.validated_data["reaction"]

        try:
            reaction = StoryReaction.objects.get(
                user=request.user,
                story=story
            )
        except StoryReaction.DoesNotExist:
            return Response(
                {"detail": "No existing reaction to update."},
                status=status.HTTP_404_NOT_FOUND
            )

        if reaction.reaction == new_reaction:
            return Response(
                {"detail": "Reaction is already set to this value."},
                status=status.HTTP_200_OK
            )

        if new_reaction == "like":
            Story.objects.filter(id=story.id).update(
                likes=F("likes") + 1,
                dislikes=F("dislikes") - 1
            )
        else:
            Story.objects.filter(id=story.id).update(
                likes=F("likes") - 1,
                dislikes=F("dislikes") + 1
            )

        reaction.reaction = new_reaction
        reaction.save(update_fields=["reaction"])

        return Response(
            {"message": "Reaction updated"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        try:
            reaction = StoryReaction.objects.get(
                user=request.user,
                story=story
            )
        except StoryReaction.DoesNotExist:
            return Response(
                {"detail": "You have not reacted to this story"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if reaction.reaction == "like":
            Story.objects.filter(id=story.id).update(likes=F("likes") - 1)
        else:
            Story.objects.filter(id=story.id).update(likes=F("dislikes") - 1)

        reaction.delete()


        return Response(status=status.HTTP_204_NO_CONTENT)