import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Author


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"},)

    class Meta: 
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

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
        read_only_fields = ['role', 'is_verified']

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
        return value


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs) 

        data['is_verified'] = self.user.is_verified
        data['role'] = self.user.role

        return data
    

class UserRoleUpdateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=["user", "admin", "moderator"])

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        username = attrs.get("username")
        new_role = attrs.get("role")

        if not user_id and not username:
            raise serializers.ValidationError("Provide either user_id or username.")

        
        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Prevent superuser from demoting themselves
        request_user = self.context["request"].user
        if user == request_user:
            raise serializers.ValidationError("You cannot change your own role.")
        

        if user.role == new_role:
            raise serializers.ValidationError(f"{user.username} already has the role '{new_role}'.")

        attrs["user_instance"] = user
        return attrs
        