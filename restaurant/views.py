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


def get_restaurant_profile(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
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
    except Restaurant.DoesNotExist:
        logger.warning("Restaurant ID could not be found: {}".format(restaurant_id))
        return HttpResponseNotFound(
            "Restaurant ID {} does not exist".format(restaurant_id)
        )


def get_inspection_info(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)

        inspection_data_list = query_inspection_record(
            restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
        )

        for i in range(len(inspection_data_list)):
            inspection_data_list[i]["inspected_on"] = inspection_data_list[i][
                "inspected_on"
            ].strftime("%Y-%m-%d %H:%M:%S")

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


def get_landing_page(request, page=0):
    restaurant_list = get_restaurant_list(page, 6)
    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
        "page": page,
    }
    return render(request, "browse.html", parameter_dict)
