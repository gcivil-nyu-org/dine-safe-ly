from django.shortcuts import render
from restaurant.utils import (
    get_restaurant_list,
)

import logging

logger = logging.getLogger(__name__)

RESTAURANT_NUMBER = 12


def index(request):
    restaurant_list = get_restaurant_list(1, RESTAURANT_NUMBER)
    parameter_dict = {
        "restaurant_list": restaurant_list,
    }
    return render(request, "index.html", parameter_dict)


def terms(request):

    return render(request, "terms.html")
