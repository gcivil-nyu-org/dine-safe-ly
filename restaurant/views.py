from django.shortcuts import render
from django.http import JsonResponse
from .models import Restaurant
from django.contrib.auth import get_user_model
from .forms import (
    QuestionnaireForm,
    SearchFilterForm,
    SaveFavoriteForm,
    DeleteFavoriteForm,
)
from .utils import (
    query_yelp,
    query_inspection_record,
    get_latest_inspection_record,
    get_restaurant_list,
    get_latest_feedback,
    get_average_safety_rating,
    get_total_restaurant_number,
    get_csv_from_s3,
    check_restaurant_saved,
)

from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello, this is restaurant.")


def get_restaurant_profile(request, restaurant_id):
    if request.method == "POST" and "save_favorite_form" in request.POST:
        form = SaveFavoriteForm(request.POST)
        if form.is_valid():
            user = get_user_model().objects.get(pk=form.cleaned_data.get("user_id"))
            user.favorite_restaurants.add(
                Restaurant.objects.get(
                    business_id=form.cleaned_data.get("restaurant_business_id")
                )
            )
    if request.method == "POST" and "delete_favorite_form" in request.POST:
        form = DeleteFavoriteForm(request.POST)
        if form.is_valid():
            user = get_user_model().objects.get(pk=form.cleaned_data.get("user_id"))
            user.favorite_restaurants.remove(
                Restaurant.objects.get(
                    business_id=form.cleaned_data.get("restaurant_business_id")
                )
            )
    if request.method == "POST" and "questionnaire_form" in request.POST:
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            form.save()

    try:
        csv_file = get_csv_from_s3()
        result = {}
        for idx, row in csv_file.iterrows():
            if idx == 0:
                continue
            result[row["modzcta"]] = [
                row["modzcta_name"],
                row["percentpositivity_7day"],
                row["people_tested"],
                row["people_positive"],
                row["median_daily_test_rate"],
                row["adequately_tested"],
            ]

        restaurant = Restaurant.objects.get(pk=restaurant_id)
        response_yelp = query_yelp(restaurant.business_id)
        latest_inspection = get_latest_inspection_record(
            restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
        )
        feedback = get_latest_feedback(restaurant.business_id)
        average_safety_rating = get_average_safety_rating(restaurant.business_id)
        if request.user.is_authenticated:
            user = request.user
            parameter_dict = {
                "google_key": settings.GOOGLE_MAP_KEY,
                "google_map_id": settings.GOOGLE_MAP_ID,
                "data": json.dumps(result, cls=DjangoJSONEncoder),
                "yelp_info": response_yelp,
                "lasted_inspection": latest_inspection,
                "restaurant_id": restaurant_id,
                "latest_feedback": feedback,
                "average_safety_rating": average_safety_rating,
                "saved_restaurants": len(
                    user.favorite_restaurants.all().filter(id=restaurant_id)
                )
                > 0,
            }
        else:
            parameter_dict = {
                "google_key": settings.GOOGLE_MAP_KEY,
                "google_map_id": settings.GOOGLE_MAP_ID,
                "data": json.dumps(result, cls=DjangoJSONEncoder),
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
            "inspection_list": inspection_data_list,
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
                form.cleaned_data.get("form_sort"),
                form.cleaned_data.get("fav"),
                request.user,
            )

            if request.user.is_authenticated:
                for restaurant in restaurant_list:
                    restaurant["saved_by_user"] = check_restaurant_saved(
                        request.user, restaurant["id"]
                    )

            restaurant_number = get_total_restaurant_number(
                form.cleaned_data.get("keyword"),
                form.cleaned_data.get("neighbourhood"),
                form.cleaned_data.get("category"),
                form.get_price_filter(),
                form.get_rating_filter(),
                form.get_compliant_filter(),
                form.cleaned_data.get("form_sort"),
                form.cleaned_data.get("fav"),
                request.user,
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
    sort_option = None
    favorite_filter = None
    user = None
    if request.user.is_authenticated:
        user = request.user
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
        sort_option,
        favorite_filter,
        user,
    )

    parameter_dict = {
        "restaurant_list": json.dumps(restaurant_list, cls=DjangoJSONEncoder),
        "page": page,
        "keyword": json.dumps({"keyword": keyword}),
    }
    return render(request, "browse.html", parameter_dict)


def save_favorite_restaurant(request, business_id):
    if request.method == "POST":
        user = request.user
        user.favorite_restaurants.add(Restaurant.objects.get(business_id=business_id))
        logger.info(business_id)
    return HttpResponse("Saved")


def delete_favorite_restaurant(request, business_id):
    if request.method == "POST":
        user = request.user
        user.favorite_restaurants.remove(
            Restaurant.objects.get(business_id=business_id)
        )
        logger.info(business_id)
        return HttpResponse("Deleted")
