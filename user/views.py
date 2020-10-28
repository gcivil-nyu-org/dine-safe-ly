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

from .forms import UserCreationForm, ResetPasswordForm, GetEmailForm

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
            print(username, password)
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
        print(user)
        if not user or not PasswordResetTokenGenerator().check_token(user, token):
            return HttpResponse("This is invalid!")
        form = ResetPasswordForm(request.POST)
        print(form)
        if form.is_valid():
            form.save(uid)
            return redirect("user:login")
        else:
            return HttpResponse("Invalid")
    else:
        form = ResetPasswordForm()
        return render(
            request=request, template_name="reset.html", context={"form": form}
        )


def forget_password(request):
    if request.method == "POST":
        form = GetEmailForm(request.POST)
        print(form)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = User.objects.get(email=email)
            base_url = "http://127.0.0.1:8000/user/reset_password/"
            url = base_url + urlsafe_base64_encode(force_bytes(user.pk)) + "/" + PasswordResetTokenGenerator().make_token(user)
            email_subject = "Reset Your Dine-safe-ly Password!"
            message = url
            email = EmailMessage(email_subject, message, to=[user.email])
            email.send()
            return render(request=request, template_name="sent_email.html")
        return render(request=request, template_name="reset_email.html", context={"form": form})
    else:
        form = GetEmailForm()
        return render(
            request=request, template_name="reset_email.html", context={"form": form}
        )
