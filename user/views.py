from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

# from django.http import HttpResponse
# from django.http import HttpResponseNotFound
# from django.core.serializers.json import DjangoJSONEncoder
# import json
# import logging
# from django.contrib.auth.models import User

# logger = logging.getLogger(__name__)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_login_page(request):
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
                return redirect("/restaurant")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, template_name="login.html", context={"form": form})


def get_register_page(request):
    return render(request, "register.html")


def post_logout(request):
    logout()
