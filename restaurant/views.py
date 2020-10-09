from django.shortcuts import get_object_or_404, render
from .models import Restaurant
from .utils import query_yelp
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core import serializers
import json


def index(request):
    return HttpResponse("Hello, this is restaurant.")


def add_inspection_records(request):
    # TODO: check login status
    records = json.loads(request.body)
    for record in serializers.deserialize("json", records):
        # TODO: Pre-process Data
        record.save()


def get_restaurant_by_name(request, restaurant_name):
    # TODO: Restaurant Model primary key haven't decided
    restaurant = Restaurant.objects.get(restaurant_name=restaurant_name)
    if not restaurant:
        # TODO: Query yelp with matching module
        return HttpResponseNotFound('Restaurant not found')
    response = query_yelp(restaurant.business_id)
    return HttpResponse(json.dumps(response))


