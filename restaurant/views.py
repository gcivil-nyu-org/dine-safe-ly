from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
import random

from .models import Restaurant

from django.views.decorators.csrf import csrf_exempt
from .forms import (
    QuestionnaireForm,
    SearchFilterForm,
)
from .utils import (
    query_yelp,
    query_inspection_record,
    get_latest_inspection_record,
    get_restaurant_list,
    get_latest_feedback,
    get_average_safety_rating,
    get_total_restaurant_number,
    check_restaurant_saved,
    get_csv_from_github,
    questionnaire_statistics,
    get_filtered_restaurants,
    restaurants_to_dict,
)

from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


def get_restaurant_profile(request, restaurant_id):

    if request.method == "POST" and "questionnaire_form" in request.POST:
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "success")
            url = reverse("restaurant:profile", args=[restaurant_id])
            return HttpResponseRedirect(url)

    try:
        csv_file = get_csv_from_github()
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

        statistics_dict = questionnaire_statistics(restaurant.business_id)
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
                "statistics_dict": statistics_dict,
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
                "statistics_dict": statistics_dict,
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
    return render(request, "browse.html")


@login_required
def save_favorite_restaurant(request, business_id):
    if request.method == "POST":
        user = request.user
        user.favorite_restaurants.add(Restaurant.objects.get(business_id=business_id))
    return HttpResponse("Saved")


@login_required
def delete_favorite_restaurant(request, business_id):
    if request.method == "POST":
        user = request.user
        user.favorite_restaurants.remove(
            Restaurant.objects.get(business_id=business_id)
        )
        return HttpResponse("Deleted")


@csrf_exempt
def chatbot_keyword(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # If user chose to be recommended by preference
            # category list is the preference list.
            if request.user and data["is_preference"]:
                data["category"] = [
                    category.category for category in request.user.preferences.all()
                ]

            restaurants = get_filtered_restaurants(
                limit=Restaurant.objects.all().count(),
                category=data["category"],
                neighborhood=data["location"],
                rating=[3.0, 3.5, 4.0, 4.5, 5.0],
                compliant="Compliant",
            )

            # If number > 3, we pick 3 random restaurants in that list to recommend to user.
            total_number = restaurants.count()
            if total_number > 3:
                idx = random.sample(range(0, total_number), 3)
                restaurants = [restaurants[i] for i in idx]

            response = {"restaurants": restaurants_to_dict(restaurants)}
            return JsonResponse(response)
        except AttributeError as e:
            return HttpResponseBadRequest(e)
