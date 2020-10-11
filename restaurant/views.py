from django.shortcuts import get_object_or_404, render
from .models import Restaurant
from .utils import query_yelp, query_inspection_record
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


def get_restaurant_by_id(request, restaurant_id):
    # TODO: Restaurant Model primary key haven't decided
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if not restaurant or not restaurant.business_id or restaurant.business_id == "":
        # TODO: Query yelp with matching module
        return HttpResponseNotFound('Restaurant not found')
    response_yelp = query_yelp(restaurant.business_id)
    inspection_data = query_inspection_record(restaurant.restaurant_name, restaurant.business_address, restaurant.postcode)
    response = {'yelp_info': response_yelp, 'opendata_info': inspection_data}
    return HttpResponse(json.dumps(response))


