from django.shortcuts import render
from .models import Restaurant
from .forms import QuestionnaireForm
from .utils import (
    query_yelp,
    query_inspection_record,
    get_latest_inspection_record,
    get_restaurant_list,
)

# from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello, this is restaurant.")


def get_restaurant_profile(request, restaurant_id):
    if request.method == "POST":
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            print("form is saved")
            form.save()
        else:
            print("form is invalid")

    # return render(request, "restaurant_detail.html", context={"form": form})
    # if request.method == "GET":
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
    neighbourhoods_filter = request.GET.getlist("neighbourhood")
    categories_filter = request.GET.getlist("category")
    keyword = request.GET.get("search")
    logger.debug(neighbourhoods_filter)
    logger.debug(categories_filter)

    restaurant_list = get_restaurant_list(
        page, 6, keyword, neighbourhoods_filter, categories_filter
    )
    logger.debug(restaurant_list)
    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
        "page": page,
        "keyword": json.dumps({"keyword": keyword}),
    }
    return render(request, "browse.html", parameter_dict)
