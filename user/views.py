from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import EmailMessage

from .forms import UserCreationForm, ResetPasswordForm

import logging

logger = logging.getLogger(__name__)


def user_login(request):
    if request.user.is_authenticated:
        return redirect("restaurant:browse")
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("restaurant:browse")
    else:
        form = AuthenticationForm()
    return render(request, template_name="login.html", context={"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("restaurant:browse")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user:login")
    else:
        form = UserCreationForm()
    return render(
        request=request, template_name="register.html", context={"form": form}
    )


@login_required
def post_logout(request):
    logout(request)
    return redirect("user:login")


def reset_password_link(request, base64_id, token):
    if request.method == "POST":
        uid = force_text(urlsafe_base64_decode(base64_id))
        user = User.objects.get(pk=uid)
        if not user or not PasswordResetTokenGenerator().check_token(user, token):
            return HttpResponse("This is invalid!")
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            form.save(uid)
        else:
            messages.error(request, "Unsuccessful. Invalid information.")
    else:
        form = ResetPasswordForm()
        return HttpResponse("Reset Password page")
    return redirect("user:login")


def forget_password(request):
    user = request.user
    base_url = "http://127.0.0.1:8000/user/reset_password/"
    url = base_url + urlsafe_base64_encode(force_bytes(user.pk)) + "/" + PasswordResetTokenGenerator().make_token(user)
    email_subject = "Reset Your Dine-safe-ly Password!"
    message = url
    email = EmailMessage(email_subject, message, to=[user.email])
    email.send()
    return HttpResponse(url)