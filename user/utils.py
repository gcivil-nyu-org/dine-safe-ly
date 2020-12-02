from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django import template

import logging

logger = logging.getLogger(__name__)


def send_reset_password_email(request, email):
    user = get_user_model().objects.get(email=email)
    host_name = request.get_host()
    base_url = "http://" + host_name + "/user/reset_password/"
    c = {
        "base_url": base_url,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": PasswordResetTokenGenerator().make_token(user),
    }
    htmltemp = template.loader.get_template("reset_password_template.html")
    html_content = htmltemp.render(c)
    email_subject = "Reset Your Dine-safe-ly Password!"
    logger.info("Send email to: %s", user.email)
    email = EmailMultiAlternatives(email_subject, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    return email.send()


def send_verification_email(request, email):
    user = get_user_model().objects.get(email=email)
    host_name = request.get_host()
    base_url = "http://" + host_name + "/user/verification/"
    logger.info(base_url)
    c = {
        "base_url": base_url,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": PasswordResetTokenGenerator().make_token(user),
    }
    htmltemp = template.loader.get_template("verify_user_template.html")
    html_content = htmltemp.render(c)
    email_subject = "Verify your account!"
    logger.info("Send email to: %s", user.email)
    email = EmailMultiAlternatives(email_subject, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    return email.send()
