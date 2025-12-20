from django.urls import path
from .views import RegisterView, LoginView, SendVerificationEmailView, VerifyEmailView, RequestPasswordResetView, PasswordResetConfirmView

urlpatterns = [ 
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("resend-email/", SendVerificationEmailView.as_view(), name="resend-email"),
    path('verify-email/', VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", RequestPasswordResetView.as_view(), name="request password reset"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='confirm password reset'),
]