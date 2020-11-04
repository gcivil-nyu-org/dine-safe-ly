from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

import logging

logger = logging.getLogger(__name__)


def send_reset_password_email(request, email):
    user = User.objects.get(email=email)
    host_name = request.get_host()
    base_url = "http://" + host_name + "/user/reset_password/"
    url = (
        base_url
        + urlsafe_base64_encode(force_bytes(user.pk))
        + "/"
        + PasswordResetTokenGenerator().make_token(user)
    )
    email_subject = "Reset Your Dine-safe-ly Password!"
    message = url
    logger.info("Send email to: %s", user.email)
    email = EmailMessage(email_subject, message, to=[user.email])
    return email.send()
