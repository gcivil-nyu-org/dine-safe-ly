from django.shortcuts import get_object_or_404, render
from .models import Restaurant
from .utils import query_yelp, query_inspection_record
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
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
    #return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder))
   # json_str = json.dumps(response, cls=DjangoJSONEncoder)
   # resp = json.loads(json_str)
    return render(request, 'home.html', {
        'name': response['yelp_info']['info']['name'],
        'img_url': response['yelp_info']['info']['image_url'],
        'link': response['yelp_info']['info']['url'],
        'phone': response['yelp_info']['info']['phone'],
        'disp_phone': response['yelp_info']['info']['display_phone'],
        'rcnt': response['yelp_info']['info']['review_count'],
        #'type:': response['yelp_info']['info']['categories']['title'],
        'rate': response['yelp_info']['info']['rating'],
        'loc': response['opendata_info']['6334']['business_address'],
        'p1': response['yelp_info']['info']['photos'][0],
        'p2': response['yelp_info']['info']['photos'][1],
        'p3': response['yelp_info']['info']['photos'][2],
        'price': response['yelp_info']['info']['price'],
        #'open': response['yelp_info']['info']['hours'],

        'r1_url': response['yelp_info']['reviews']['reviews'][0]['url'],
        'r1_text': response['yelp_info']['reviews']['reviews'][0]['text'],
        'r1_rate': response['yelp_info']['reviews']['reviews'][0]['rating'],
        'r1_time': response['yelp_info']['reviews']['reviews'][0]['time_created'],
        'r1_user_name': response['yelp_info']['reviews']['reviews'][0]['user']['name'],
        'r1_user_url': response['yelp_info']['reviews']['reviews'][0]['user']['profile_url'],
        'r1_user_img': response['yelp_info']['reviews']['reviews'][0]['user']['image_url'],

        'r2_url': response['yelp_info']['reviews']['reviews'][1]['url'],
        'r2_text': response['yelp_info']['reviews']['reviews'][1]['text'],
        'r2_rate': response['yelp_info']['reviews']['reviews'][1]['rating'],
        'r2_time': response['yelp_info']['reviews']['reviews'][1]['time_created'],
        'r2_user_name': response['yelp_info']['reviews']['reviews'][1]['user']['name'],
        'r2_user_url': response['yelp_info']['reviews']['reviews'][1]['user']['profile_url'],
        'r2_user_img': response['yelp_info']['reviews']['reviews'][1]['user']['image_url'],

        'r3_url': response['yelp_info']['reviews']['reviews'][2]['url'],
        'r3_text': response['yelp_info']['reviews']['reviews'][2]['text'],
        'r3_rate': response['yelp_info']['reviews']['reviews'][2]['rating'],
        'r3_time': response['yelp_info']['reviews']['reviews'][2]['time_created'],
        'r3_user_name': response['yelp_info']['reviews']['reviews'][2]['user']['name'],
        'r3_user_url': response['yelp_info']['reviews']['reviews'][2]['user']['profile_url'],
        'r3_user_img': response['yelp_info']['reviews']['reviews'][2]['user']['image_url'],

        'total_reviews': response['yelp_info']['reviews']['total'],
        'lat': response['yelp_info']['info']['coordinates']['latitude'],
        'long': response['yelp_info']['info']['coordinates']['longitude'],

        #Compliance data
        'seating_choice': response['opendata_info']['6334']['seating_choice'],
        'is_sideway_compliant': response['opendata_info']['6334']['is_sideway_compliant'],
        'is_roadway_compliant': response['opendata_info']['6334']['is_roadway_compliant'],
        'inspected_on': response['opendata_info']['6334']['inspected_on'],
        'skipped_reason': response['opendata_info']['6334']['skipped_reason']
    })