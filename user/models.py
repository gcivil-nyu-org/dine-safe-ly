from django.db import models
from django.contrib.auth.models import AbstractUser
from restaurant.models import Restaurant


class DineSafelyUser(AbstractUser):

    favorite_restaurants = models.ManyToManyField(Restaurant, blank=True)
