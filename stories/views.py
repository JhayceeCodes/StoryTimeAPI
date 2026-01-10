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
from django.db.models import Avg, Count
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from datetime import timedelta
from django.utils import timezone
from accounts.permissions import IsVerified
from .serializers import StorySerializer, ReactionSerializer, ReviewSerializer, RatingSerializer
from .models import Story, Reaction, Review, Rating
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

        if self.action == "partial_update":
            return [IsStoryOwner()]

        if self.action == "destroy":
            return [CanDeleteStory()]

        return [IsAuthenticated()]
    
    
    def list(self, request, *args, **kwargs):
        cache_key = "stories:list"
        data = cache.get(cache_key)

        if data:
            return Response(data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)
        return response
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user.author)
        cache.delete("stories:list")

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete("stories:list")
        cache.delete(f"story:{instance.id}")

    def put(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use PATCH to update a story."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    

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

        _ , created = Reaction.objects.get_or_create(
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
            {"message": "Reaction updated."},
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def delete(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        try:
            reaction = Reaction.objects.get(
                user=request.user,
                story=story
            )
        except Reaction.DoesNotExist:
            return Response(
                {"detail": "Reaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if reaction.reaction == "like":
            Story.objects.filter(id=story.id).update(likes=F("likes") - 1)
        else:
            Story.objects.filter(id=story.id).update(delete=F("dislikes") - 1)

        reaction.delete()


        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = ReviewsPagination

    def get_queryset(self):
        return Review.objects.filter(
            story_id=self.kwargs.get("story_pk")
        ).select_related("story")

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsVerified()]
        if self.action == "partial_update":
            return [IsReviewOwner()]
        if self.action == "destroy":
            return [CanDeleteReview() or IsReviewOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        story = get_object_or_404(Story, id=self.kwargs.get("story_pk"))
        serializer = serializer.__class__(
            data=self.request.data,
            context={**self.get_serializer_context(), "story": story}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, story=story)


    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        if timezone.now() - review.created_at > timedelta(minutes=30):
            return Response(
                {"detail": "User can only update a review within 30 minutes."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use PATCH to update a story."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )



class RatingView(APIView):
    permission_classes = [IsVerified]

    @transaction.atomic
    def post(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        if request.user == story.author.user:
            return Response(
                {"detail": "Authors cannot rate their own story"},
                status=status.HTTP_400_BAD_REQUEST
            )


        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if Rating.objects.filter(user=request.user, story=story).exists():
            return Response(
                {"detail": "Rating already exists. Use PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Rating.objects.create(
            user=request.user,
            story=story,
            rating=serializer.validated_data["rating"]
        )

        self._update_story_rating(story)

        return Response(
            {"message": "Rating added successfully."},
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def patch(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        serializer = RatingSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        updated = Rating.objects.filter(
            user=request.user,
            story=story
        ).update(rating=serializer.validated_data["rating"])

        if not updated:
            return Response(
                {"detail": "Rating not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        self._update_story_rating(story)

        return Response(
            {"message": "Rating updated successfully."},
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def delete(self, request, story_id):
        story = get_object_or_404(Story, id=story_id)

        try:
            rating = Rating.objects.get(user=request.user, story=story)
            rating.delete()

            self._update_story_rating(story)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Rating.DoesNotExist:
            return Response(
                {"detail": "Rating not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    def _update_story_rating(self, story):
        agg = Rating.objects.filter(story=story).aggregate(
            avg=Avg("rating"),
            count=Count("id")
        )
        Story.objects.filter(id=story.id).update(
            total_ratings=agg["count"] or 0,
            average_rating=agg["avg"] or 0
        )
