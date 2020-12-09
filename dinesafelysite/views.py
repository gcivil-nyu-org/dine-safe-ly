from django.shortcuts import render
from restaurant.utils import get_compliant_restaurant_list

import logging

logger = logging.getLogger(__name__)

RESTAURANT_NUMBER = 18


def index(request):
    restaurant_list = get_compliant_restaurant_list(
        1,
        RESTAURANT_NUMBER,
        rating_filter=[3, 3.5, 4, 4.5, 5],
        compliant_filter="Compliant",
    )
    parameter_dict = {
        "restaurant_list": restaurant_list,
    }
    return render(request, "index.html", parameter_dict)


def terms(request):
    return render(request, "terms.html")
