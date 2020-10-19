from django.conf import settings
from django.forms.models import model_to_dict
from .models import InspectionRecords, Restaurant
import requests
import json


def get_restaurant_info_yelp(business_id):
    access_token = settings.YELP_ACCESS_TOKE
    headers = {'Authorization': 'bearer %s' % access_token}
    url = settings.YELP_BUSINESS_API + business_id
    return requests.get(url, headers=headers)


def get_restaurant_reviews_yelp(business_id):
    access_token = settings.YELP_ACCESS_TOKE
    headers = {'Authorization': 'bearer %s' % access_token}
    url = settings.YELP_BUSINESS_API + business_id + '/reviews'
    return requests.get(url, headers=headers)


def query_yelp(business_id):
    if not business_id:
        return None
    restaurant_info = get_restaurant_info_yelp(business_id)
    restaurant_reviews = get_restaurant_reviews_yelp(business_id)
    data = {
        'info': json.loads(restaurant_info.content),
        'reviews': json.loads(restaurant_reviews.content)
    }
    return data


def get_latest_inspection_record(business_name, business_address, postcode):
    records = InspectionRecords.objects.filter(restaurant_name=business_name, business_address=business_address,
                                               postcode=postcode).order_by('-inspected_on')
    if len(records) >= 1:
        return model_to_dict(records[0])

    return None


def query_inspection_record(business_name, business_address, postcode):
    records = InspectionRecords.objects.filter(restaurant_name=business_name, business_address=business_address,
                                               postcode=postcode).order_by('-inspected_on')
    result = []
    for record in records:
        result.append(model_to_dict(record))
    return result


def get_restaurant_list(page, limit):
    offset = int(page) * int(limit)
    restaurants = Restaurant.objects.all()[offset: offset + int(limit)]
    result = []
    for restaurant in restaurants:
        restaurant_dict = model_to_dict(restaurant)
        restaurant_dict['yelp_info'] = json.loads(get_restaurant_info_yelp(restaurant.business_id).content) if restaurant.business_id else None
        result.append(restaurant_dict)
    return result

