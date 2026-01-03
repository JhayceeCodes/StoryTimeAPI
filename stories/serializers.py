from rest_framework import serializers
from .models import Story, Reaction, Review, Rating

class StorySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.pen_name", read_only=True)
    class Meta:
        model = Story
        fields = ["id", "title", "content", "author", "genre", "likes", "dislikes", "average_rating", "total_ratings", "created_at"]
        read_only_fields = ["author", "created_at", "likes", "dislikes", "average_rating", "total_ratings"]
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least three characters long.")
        return value
    
    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["reaction"]

    def validate_reaction(self, value):
        if value not in ("like", "dislike"):
            raise serializers.ValidationError(
                "Reaction must be either 'like' or 'dislike'."
            )
        return value
    

class ReviewSerializer(serializers.ModelSerializer):
    story = serializers.CharField(source="story.title", read_only=True)
    class Meta:
        model = Review
        fields = ["id", "story", "content", "alias", "created_at"]
        read_only_fields = ["story", "created_at"]
    
    def validate(self, attrs):
        user = self.context["request"].user
        story = self.context.get("story")
        alias = attrs.get("alias") or user.username

        if Review.objects.filter(story=story, alias=alias).exists():
            raise serializers.ValidationError(
                {"alias": "This alias already exists for this story."}
            )

        if Review.objects.filter(story=story, user=user).exists():
            raise serializers.ValidationError(
                {"user": "You have already reviewed this story."}
            )

        return attrs

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["rating"]

    

    


   
