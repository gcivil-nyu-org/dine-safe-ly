from django.shortcuts import get_object_or_404, render
from .models import Restaurant
import requests
from django.http import HttpResponse
import json


# Create your views here.
def index(request):
    return HttpResponse("Hello, this is restaurant.")

def get_restaurant_by_name(request, restaurant_name):
    restaurant = get_object_or_404(Restaurant, restaurant_name=restaurant_name)
    business_id = restaurant.business_id
    access_token = 'A_V_V4rxelsvDsI2uFW1kT2mP2lUjd75GTEEsEcLnnvVOK5ssemrbw-R49czpANtS2ZtAeCl6FaapQrp1_30cRt9YKao3pFL1I6304sAtwKwKJkF1JBgF88FZl1_X3Yx'
    headers = {'Authorization': 'bearer %s' % access_token}
    response = {}
    response['info'] = json.loads(requests.get('https://api.yelp.com/v3/businesses/' + business_id, headers=headers).content)
    response['reviews'] = json.loads(requests.get('https://api.yelp.com/v3/businesses/' + business_id + '/reviews', headers=headers).content)
    return HttpResponse(json.dumps(response))

