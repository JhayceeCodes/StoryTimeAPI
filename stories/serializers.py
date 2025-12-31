from rest_framework import serializers
from .models import Story, Reaction, Review

class StorySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.pen_name")
    content = serializers.CharField(max_length=3000)
    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = ["author", "content", "created_at", "likes", "dislikes"]
    
    def validate__title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least three characters long.")
        return value


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["reaction", "story", "updated_at"]
        read_only_fields = ["story", "updated_at"]


    
    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None
        story = attrs.get("story")

        if Reaction.objects.filter(user= user, story=story).exists():
            raise serializers.ValidationError(
                "You have already reacted to this s..tory."
            )
        return attrs

    def validate_reaction(self, value):
        if value not in ("like", "dislike"):
            raise serializers.ValidationError(
                "Reaction must be either 'like' or 'dislike'."
            )
        return value
    

class ReviewSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=500)
    class Meta:
        model = Review
        fields = ["content", "story", "alias", "created_at"]
        read_only_fields = ["created_at"]
        


   
