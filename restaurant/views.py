from django.shortcuts import render
from django.http import JsonResponse
from .models import Restaurant
from .forms import QuestionnaireForm, SearchFilterForm
from .utils import (
    query_yelp,
    query_inspection_record,
    get_latest_inspection_record,
    get_restaurant_list,
    get_latest_feedback,
    get_average_safety_rating,
    get_total_restaurant_number,
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
        print(form.is_valid())
        logger.info(form.is_valid())
        if form.is_valid():
            form.save()
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        response_yelp = query_yelp(restaurant.business_id)
        latest_inspection = get_latest_inspection_record(
            restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
        )
        feedback = get_latest_feedback(restaurant.business_id)
        average_safety_rating = get_average_safety_rating(restaurant.business_id)
        parameter_dict = {
            "yelp_info": response_yelp,
            "lasted_inspection": latest_inspection,
            "restaurant_id": restaurant_id,
            "latest_feedback": feedback,
            "average_safety_rating": average_safety_rating,
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


def get_restaurants_list(request, page):
    if request.method == "POST":
        form = SearchFilterForm(request.POST)

        if form.is_valid():
            restaurant_list = get_restaurant_list(
                page,
                6,
                form.cleaned_data.get("keyword"),
                form.cleaned_data.get("neighbourhood"),
                form.cleaned_data.get("category"),
                form.get_price_filter(),
                form.get_rating_filter(),
                form.get_compliant_filter(),
            )
            restaurant_number = get_total_restaurant_number(
                form.cleaned_data.get("keyword"),
                form.cleaned_data.get("neighbourhood"),
                form.cleaned_data.get("category"),
                form.get_price_filter(),
                form.get_rating_filter(),
                form.get_compliant_filter(),
            )
            parameter_dict = {
                "restaurant_number": restaurant_number,
                "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
                "page": page,
            }
            return JsonResponse(parameter_dict)
        else:
            logger.error(form.errors)
    return HttpResponse("cnm")


def get_landing_page(request, page=1):
    neighbourhoods_filter = request.GET.getlist("neighbourhood")
    categories_filter = request.GET.getlist("category")
    price_filter = request.GET.getlist("price")
    rating_filter = None
    compliant_filter = None
    if request.GET.getlist("ratingfrom"):
        rating_filter = float(request.GET.getlist("ratingfrom")[0])
    keyword = request.GET.get("search")

    restaurant_list = get_restaurant_list(
        page,
        12,
        keyword,
        neighbourhoods_filter,
        categories_filter,
        price_filter,
        rating_filter,
        compliant_filter,
    )

    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
        "page": page,
        "keyword": json.dumps({"keyword": keyword}),
    }
    return render(request, "browse.html", parameter_dict)
