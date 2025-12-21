from django.urls import path
from .views import RegisterView, LoginView, SendVerificationEmailView, VerifyEmailView, RequestPasswordResetView, PasswordResetConfirmView, AuthorView, RegisterAuthorView

urlpatterns = [ 
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("resend-email/", SendVerificationEmailView.as_view(), name="resend-email"),
    path('verify-email/', VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", RequestPasswordResetView.as_view(), name="request password reset"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='confirm password reset'),
    path('register-author/', RegisterAuthorView.as_view(), name="register author"),
    path('authors/me/', AuthorView.as_view(), name="fetch or update author information")
]