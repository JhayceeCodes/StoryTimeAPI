import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Author


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"},)

    class Meta: 
        model = User
        fields = ['username', 'email', 'password']
    

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['pen_name', 'ban_status']
        read_only_fields = ['ban_status']

    
    def validate_pen_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Pen name must be at least 3 characters long."
            )

        if len(value) > 50:
            raise serializers.ValidationError(
                "Pen name must not exceed 50 characters."
            )

        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise serializers.ValidationError(
                "Pen name must contain letters only."
            )

        return value

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_verified', 'role']
        read_only_fields = ['role']
