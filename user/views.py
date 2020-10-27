from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def user_login(request):
    if request.method == "GET":
        return render(request, "login.html")
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect("restaurant:browse")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, template_name="login.html", context={"form": form})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request=request, data=request.POST)
        if form.is_valid():
            form.save()
            # login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("user:login")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    form = CustomUserCreationForm()
    return render(
        request=request, template_name="register.html", context={"form": form}
    )


def post_logout(request):
    logout()
