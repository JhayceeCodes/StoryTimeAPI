from rest_framework import serializers
from .models import Story, StoryReaction

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = ["author", "created_at", "likes", "dislikes"]
    
    def validate__title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least three characters long.")
        return value


class StoryReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryReaction
        fields = "__all__"
        read_only_fields = ["user", "updated_at"]

    
    def validate(self, attrs):
        user = self.context.get["request"].user
        story = attrs.get("story")

        if StoryReaction.objects.filter(user= user, story=story).exists():
            raise serializers.ValidationError(
                "You have already reacted to this story."
            )
        return attrs