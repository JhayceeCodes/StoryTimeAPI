from django.urls import path
from .views import RegisterView, SendVerificationEmailView, VerifyEmailView, RequestPasswordResetView, PasswordResetConfirmView, AuthorView, RegisterAuthorView, LogoutView, LoginView, ProfileView, UpdateUserRoleView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [ 
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("resend-email/", SendVerificationEmailView.as_view(), name="resend_email"),
    path("verify/<uid>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("password-reset/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    path("reset/<uid>/<token>/", PasswordResetConfirmView.as_view(), name='confirm_password_reset'),
    path("register-author/", RegisterAuthorView.as_view(), name="register_author"),
    path("authors/me/", AuthorView.as_view(), name="fetch_or_update_author_info"),
    path("users/role/", UpdateUserRoleView.as_view(), name="update_user_role")
]