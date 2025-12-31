from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F
from django.db import transaction
from django.shortcuts import get_object_or_404
from .serializers import StorySerializer, ReactionSerializer, ReviewSerializer
from .models import Story, Reaction, Review
from .permissions import IsAuthor, IsStoryOwner, CanDeleteStory, IsReviewOwner, CanDeleteReview
from .pagination import ReviewsPagination
from .filters import StoryFilter

""""
- All users, authenticated or not, can read stories
- Only authors can create story 
- Any update can only be done by story author
- Delete can be done by the story author, moderator, or admin
"""
class StoryViewSet(ModelViewSet):
    queryset =Story.objects.all().select_related("author")
    serializer_class = StorySerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = StoryFilter

    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "likes", "dislikes"]
    ordering = ["-created_at"]

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

class ReactionView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, story_id):

        story = get_object_or_404(Story, id=story_id)

        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction_type = serializer.validated_data["reaction"]

        reaction, created = Reaction.objects.get_or_create(
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

        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_reaction = serializer.validated_data["reaction"]

        try:
            reaction = Reaction.objects.get(
                user=request.user,
                story=story
            )
        except Reaction.DoesNotExist:
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
            reaction = Reaction.objects.get(
                user=request.user,
                story=story
            )
        except Reaction.DoesNotExist:
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
    

class ReviewViewSet(ModelViewSet):
    queryset =Review.objects.all().select_related("story")
    serializer_class = ReviewSerializer
    pagination_class = ReviewsPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]

        if self.action == "partial_update":
            return [IsReviewOwner()]
        
        if self.action == "destroy":
            return [CanDeleteReview()]

        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        review = self.get_object()
        time_limit = timedelta(minutes=30) 
        if timezone.now() - review.created_at > time_limit:
            return Response(
                {"detail": "You can only update a review within 30 minutes of posting."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()