import os
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .serializers import RegisterSerializer, AuthorSerializer, ProfileSerializer
from .tasks import send_password_reset_email_task, send_verification_email_task
from .utils import generate_token, verify_token
from .models import  User
from .permissions import IsVerified

frontend_url = os.getnv("FRONTEND_URL", "http://127.0.0.1:8000")

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        uid, token = generate_token(user)
        verify_link = f"{frontend_url}/verify-email/{uid}/{token}"
        send_verification_email_task.delay(user.id, verify_link)
    
        

class SendVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_verified:
            return Response(
                {'message': 'Email is already verified'},
                status=status.HTTP_200_OK
            )

        uid, token = generate_token(user)
        verify_link = f"{frontend_url}/accounts/verify/{uid}/{token}/"

        send_verification_email_task.delay(user.id, verify_link)

        return Response(
            {'message': 'Verification email sent'},
            status=status.HTTP_200_OK
        )
        

class VerifyEmailView(APIView):
    def get(self, request, uid, token):
        user = verify_token(uid, token)

        if not user:
            return Response(
                {'detail': 'Invalid or expired verification link.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_verified:
            return Response(
                {'detail': 'Email already verified.'},
                status=status.HTTP_200_OK
            )

        
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return Response(
            {'message': 'Email verified successfully.'},
            status=status.HTTP_200_OK
        )

    
class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

        uid, token = generate_token(user)
        
        reset_link = f"{frontend_url}/reset/{uid}/{token}/"
        
        send_password_reset_email_task.delay(user.id, reset_link)

        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

    
class PasswordResetConfirmView(APIView):
    permission_classes = []

    def post(self, request, uid, token):
        user = verify_token(uid, token)

        if not user:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_password = request.data.get("password")
        if not new_password:
            return Response(
                {"detail": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK
        )


class AuthorView(generics.RetrieveUpdateAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.author

class RegisterAuthorView(generics.CreateAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "author"):
            return Response(
                {"detail": "Author profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_205_RESET_CONTENT
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user