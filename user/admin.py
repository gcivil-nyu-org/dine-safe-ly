from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.admin import UserAdmin
from .models import MyUser


admin.site.register(MyUser, UserAdmin)



