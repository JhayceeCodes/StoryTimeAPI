from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginSerializer
from .tasks import send_password_reset_email_task, send_verification_email_task
from .utils import generate_token, verify_token



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        uid, token = generate_token(user)
        verify_link = f"/verify-email/..."
        send_verification_email_task.delay(user.id, verify_link)
    
        
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer