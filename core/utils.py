import os
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email(to_email, subject, template_name, context):
    html_content = render_to_string(template_name, context)

    try:
        html_content = render_to_string(template_name, context)

        text_content = (
            html_content.replace("<br>", "\n")
            .replace("<br/>", "\n")
            .replace("<strong>", "")
            .replace("</strong>", "")
            .strip()
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info("Email sent successfully to %s | subject=%s", to_email, subject)
        return True

    except Exception:
        logger.exception("Email sending failed | subject=%s | to=%s", subject, to_email)
        return False