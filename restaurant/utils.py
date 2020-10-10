from django.conf import settings
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
    restaurant_info = get_restaurant_info_yelp(business_id)
    restaurant_reviews = get_restaurant_reviews_yelp(business_id)
    data = {
        'info': json.loads(restaurant_info.content),
        'reviews': json.loads(restaurant_reviews.content)
    }
    return data

