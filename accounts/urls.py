from django.urls import path
from .views import RegisterView, LoginView, SendVerificationEmailView, VerifyEmailView

urlpatterns = [ 
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("resend-email/", SendVerificationEmailView.as_view(), name="resend-email"),
    path('verify-email/', VerifyEmailView.as_view(), name="verify-email")
]