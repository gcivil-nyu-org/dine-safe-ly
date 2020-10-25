from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.admin import UserAdmin


class MyUser(AbstractUser):
    pass
