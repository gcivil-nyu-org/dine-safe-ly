from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import UserCreationForm

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
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
                messages.error(request, "Invalid username")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, template_name="login.html", context={"form": form})


@csrf_exempt
def register(request):
    if request.user.is_authenticated:
        return redirect("restaurant:browse")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user:login")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    form = UserCreationForm()
    return render(
        request=request, template_name="register.html", context={"form": form}
    )


def post_logout(request):
    logout(request)
    return redirect("user:login")
