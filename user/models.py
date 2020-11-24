from django.db import models
from django.contrib.auth.models import AbstractUser
from restaurant.models import Restaurant, Categories


class DineSafelyUser(AbstractUser):
    favorite_restaurants = models.ManyToManyField(Restaurant, blank=True)
    preferences = models.ManyToManyField(Categories, blank=True)
