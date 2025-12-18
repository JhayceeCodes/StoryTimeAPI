import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from core.utils import send_email

logger = logging.getLogger(__name__)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


def send_verification_email(user, verify_link):
    subject = "Verify Your Email – Story.::.Time"
    context = {"user": user, "verify_link": verify_link}

    send_email(
        to_email=user.email,
        subject=subject,
        template_name="emails/verify_email.html",
        context=context,
    )
    #logger.info("Verification email sent")
    


def send_password_reset_email(user, reset_link):
    subject = "Password Reset – Story.::.Time"
    context = {"user": user, "reset_link": reset_link}

    send_email(
        to_email=user.email,
        subject=subject,
        template_name="emails/password_reset.html",
        context=context,
    )
    #logger.info("Password reset email sent")


def generate_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    return uid, token

def verify_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        return user
    return None