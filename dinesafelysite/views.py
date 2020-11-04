from django.shortcuts import render
from restaurant.utils import (
    get_restaurant_list,
)
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)

RESTAURANT_NUMBER = 12


def index(request):
    restaurant_list = get_restaurant_list(1, RESTAURANT_NUMBER)
    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
    }
    return render(request, "index.html", parameter_dict)