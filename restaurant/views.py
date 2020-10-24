from django.shortcuts import render
from .models import Restaurant
from .utils import (
    query_yelp,
    query_inspection_record,
    get_latest_inspection_record,
    get_restaurant_list,
)
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello, this is restaurant.")


def get_restaurant_by_id(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)

    # if not restaurant.business_id:
    #     parameter_dict = {'restaurant':restaurant}
    #     return render(request, 'dummy_restaurant.html', parameter_dict)

    if not restaurant or not restaurant.business_id:
        # TODO: Query yelp with matching module
        return HttpResponseNotFound("Restaurant not found")
    response_yelp = query_yelp(restaurant.business_id)
    latest_inspection = get_latest_inspection_record(
        restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
    )
    parameter_dict = {
        "yelp_info": response_yelp,
        "lasted_inspection": latest_inspection,
        "restaurant_id": restaurant_id,
    }
    return render(request, "restaurant_detail.html", parameter_dict)

    # if 'price' not in response['yelp_info']['info']:
    #     return render(request, 'home.html', {
    #         'restaurant_id': response['restaurant_id'],
    #         'name': response['yelp_info']['info']['name'],
    #         'img_url': response['yelp_info']['info']['image_url'],
    #         'link': response['yelp_info']['info']['url'],
    #         'phone': response['yelp_info']['info']['phone'],
    #         'disp_phone': response['yelp_info']['info']['display_phone'],
    #         'rcnt': response['yelp_info']['info']['review_count'],
    #         # 'type:': response['yelp_info']['info']['categories']['title'],
    #         'rate': response['yelp_info']['info']['rating'],
    #         'loc': response['opendata_info']['business_address'],
    #         'p1': response['yelp_info']['info']['photos'][0],
    #         'p2': response['yelp_info']['info']['photos'][1],
    #         'p3': response['yelp_info']['info']['photos'][2],
    #         # Compliance data
    #         # 'seating_choice': response['opendata_info']['seating_choice'],
    #         # 'is_sideway_compliant': response['opendata_info']['6334']['is_sideway_compliant'],
    #         'is_roadway_compliant': response['opendata_info']['is_roadway_compliant'],
    #         'inspected_on': response['opendata_info']['inspected_on'],
    #         'skipped_reason': response['opendata_info']['skipped_reason']})
    # try:
    #     return render(request, 'home.html', {
    #         'restaurant_id': response['restaurant_id'],
    #         'name': response['yelp_info']['info']['name'],
    #         'img_url': response['yelp_info']['info']['image_url'],
    #         'link': response['yelp_info']['info']['url'],
    #         'phone': response['yelp_info']['info']['phone'],
    #         'disp_phone': response['yelp_info']['info']['display_phone'],
    #         'rcnt': response['yelp_info']['info']['review_count'],
    #         # 'type:': response['yelp_info']['info']['categories']['title'],
    #         'rate': response['yelp_info']['info']['rating'],
    #         'loc': response['opendata_info']['business_address'],
    #         'p1': response['yelp_info']['info']['photos'][0],
    #         'p2': response['yelp_info']['info']['photos'][1],
    #         'p3': response['yelp_info']['info']['photos'][2],
    #         'price': response['yelp_info']['info']['price'],
    #         # 'open': response['yelp_info']['info']['hours'],
    #
    #         # response = {'yelp_info': response_yelp}
    #         # return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder))
    #
    #         'r1_url': response['yelp_info']['reviews']['reviews'][0]['url'],
    #         'r1_text': response['yelp_info']['reviews']['reviews'][0]['text'],
    #         'r1_rate': response['yelp_info']['reviews']['reviews'][0]['rating'],
    #         'r1_time': response['yelp_info']['reviews']['reviews'][0]['time_created'],
    #         'r1_user_name': response['yelp_info']['reviews']['reviews'][0]['user']['name'],
    #         'r1_user_url': response['yelp_info']['reviews']['reviews'][0]['user']['profile_url'],
    #         'r1_user_img': response['yelp_info']['reviews']['reviews'][0]['user']['image_url'],
    #
    #         'r2_url': response['yelp_info']['reviews']['reviews'][1]['url'],
    #         'r2_text': response['yelp_info']['reviews']['reviews'][1]['text'],
    #         'r2_rate': response['yelp_info']['reviews']['reviews'][1]['rating'],
    #         'r2_time': response['yelp_info']['reviews']['reviews'][1]['time_created'],
    #         'r2_user_name': response['yelp_info']['reviews']['reviews'][1]['user']['name'],
    #         'r2_user_url': response['yelp_info']['reviews']['reviews'][1]['user']['profile_url'],
    #         'r2_user_img': response['yelp_info']['reviews']['reviews'][1]['user']['image_url'],
    #
    #         'r3_url': response['yelp_info']['reviews']['reviews'][2]['url'],
    #         'r3_text': response['yelp_info']['reviews']['reviews'][2]['text'],
    #         'r3_rate': response['yelp_info']['reviews']['reviews'][2]['rating'],
    #         'r3_time': response['yelp_info']['reviews']['reviews'][2]['time_created'],
    #         'r3_user_name': response['yelp_info']['reviews']['reviews'][2]['user']['name'],
    #         'r3_user_url': response['yelp_info']['reviews']['reviews'][2]['user']['profile_url'],
    #         'r3_user_img': response['yelp_info']['reviews']['reviews'][2]['user']['image_url'],
    #
    #         'total_reviews': response['yelp_info']['reviews']['total'],
    #         'lat': response['yelp_info']['info']['coordinates']['latitude'],
    #         'long': response['yelp_info']['info']['coordinates']['longitude'],
    #
    #         # Compliance data
    #         # 'seating_choice': response['opendata_info']['seating_choice'],
    #         # 'is_sideway_compliant': response['opendata_info']['6334']['is_sideway_compliant'],
    #         'is_roadway_compliant': response['opendata_info']['is_roadway_compliant'],
    #         'inspected_on': response['opendata_info']['inspected_on'],
    #         'skipped_reason': response['opendata_info']['skipped_reason']
    #     })
    # except:
    #     return HttpResponseNotFound('Restaurant not found')


def get_inspection_info(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)

        inspection_data_list = query_inspection_record(
            restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
        )

        parameter_dict = {
            "inspection_list": json.dumps(inspection_data_list, cls=DjangoJSONEncoder),
            "restaurant_id": restaurant_id,
        }

        return render(request, "inspection_records.html", parameter_dict)
    except Restaurant.DoesNotExist:
        logger.warning("Restaurant ID could not be found: {}".format(restaurant_id))
        return HttpResponseNotFound(
            "Restaurant ID {} does not exist".format(restaurant_id)
        )


def get_landing_page(request, page):
    restaurant_list = get_restaurant_list(page, 6)
    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
        "page": page,
    }
    return render(request, "browse.html", parameter_dict)
