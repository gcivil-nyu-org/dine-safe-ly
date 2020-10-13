from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from .models import Restaurant, InspectionRecords
from .utils import query_yelp, query_inspection_record
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json


def index(request):
    return HttpResponse("Hello, this is restaurant.")


@csrf_exempt
def add_inspection_records(request):
    # # TODO: check login status
    records = json.loads(request.body)
    for record in records:
        inspection_record = InspectionRecords(restaurant_Inspection_ID=record['restaurant_Inspection_ID'],
                                              restaurant_name=record['restaurant_name'],
                                              legal_business_name=record['legal_business_name'],
                                              business_address=record['business_address'],
                                              inspected_on=record['inspected_on'],
                                              postcode=record['postcode'])
        inspection_record.save()
    return HttpResponse("Add inspection records")


def get_restaurant_by_id(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if not restaurant or not restaurant.business_id:
        # TODO: Query yelp with matching module
        return HttpResponseNotFound('Restaurant not found')
    response_yelp = query_yelp(restaurant.business_id)

    response = {'yelp_info': response_yelp}
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder))


def get_inspection_info(request, name, address, postcode):
    inspection_data = query_inspection_record(name, address, postcode)
    response = {'opendata_info': inspection_data}
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder))
