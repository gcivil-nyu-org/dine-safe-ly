from django.conf import settings
from django.forms.models import model_to_dict
from .models import (
    InspectionRecords,
    Restaurant,
    YelpRestaurantDetails,
    UserQuestionnaire,
)
import requests
import json
import logging
import pandas as pd
import io

logger = logging.getLogger(__name__)


def get_restaurant_info_yelp(business_id):
    access_token = settings.YELP_ACCESS_TOKEN_BUSINESS_ID
    headers = {"Authorization": "bearer %s" % access_token}
    url = settings.YELP_BUSINESS_API + business_id
    return requests.get(url, headers=headers)


def default_info_page(restaurant_name):
    return {
        "name": restaurant_name,
        "image_url": settings.DEFAULT_IMAGE,
        "rating": 0,
        "fake_info": True,
    }


def get_restaurant_info_yelp_local(business_id, restaurant_name):
    yelp_detail_set = YelpRestaurantDetails.objects.filter(business_id=business_id)[0:1]
    if yelp_detail_set.count() == 0:
        return json.loads(get_restaurant_info_yelp(business_id).content)
    yelp_detail = yelp_detail_set[0]
    yelp_dict = model_to_dict(yelp_detail) if yelp_detail else None
    if yelp_dict:
        # Format the info
        yelp_dict["rating"] = yelp_dict["rating"] if yelp_dict["rating"] else 0
        yelp_dict["price"] = yelp_dict["price"] if yelp_dict["price"] else ""
        yelp_dict["id"] = yelp_dict["business_id"]
        yelp_dict["name"] = restaurant_name
        yelp_dict["image_url"] = (
            yelp_dict["img_url"] if yelp_dict["img_url"] else settings.DEFAULT_IMAGE
        )
        category_list = []
        for category in yelp_dict["category"]:
            category_list.append({"title": category.parent_category})
        del yelp_dict["category"]
        yelp_dict["categories"] = category_list

    return yelp_dict


def get_restaurant_reviews_yelp(business_id):
    access_token = settings.YELP_ACCESS_TOKEN_REVIEW
    headers = {"Authorization": "bearer %s" % access_token}
    url = settings.YELP_BUSINESS_API + business_id + "/reviews"
    return requests.get(url, headers=headers)


def merge_yelp_info(restaurant_info, restaurant_reviews):
    yelp_info = json.loads(restaurant_info.content)
    yelp_info["rating"] = yelp_info["rating"] if "rating" in yelp_info else 0
    yelp_info["price"] = yelp_info["price"] if "price" in yelp_info else ""
    yelp_info["image_url"] = (
        yelp_info["image_url"] if "image_url" in yelp_info else settings.DEFAULT_IMAGE
    )
    return {
        "info": yelp_info,
        "reviews": json.loads(restaurant_reviews.content),
    }


def query_yelp(business_id):
    if not business_id:
        return None
    restaurant_info = get_restaurant_info_yelp(business_id)
    restaurant_reviews = get_restaurant_reviews_yelp(business_id)

    data = merge_yelp_info(restaurant_info, restaurant_reviews)
    return data


def get_latest_inspection_record(business_name, business_address, postcode):
    records = InspectionRecords.objects.filter(
        restaurant_name=business_name,
        business_address=business_address,
        postcode=postcode,
    ).order_by("-inspected_on")
    if len(records) >= 1:
        record = model_to_dict(records[0])
        record["inspected_on"] = record["inspected_on"].strftime("%Y-%m-%d %I:%M %p")
        return record

    return None


def query_inspection_record(business_name, business_address, postcode):
    records = InspectionRecords.objects.filter(
        restaurant_name=business_name,
        business_address=business_address,
        postcode=postcode,
    ).order_by("-inspected_on")
    result = []
    for record in records:
        inspection_record = model_to_dict(record)
        inspection_record["inspected_on"] = inspection_record["inspected_on"].strftime(
            "%Y-%m-%d %I:%M %p"
        )
        result.append(inspection_record)

    return result


def restaurants_to_dict(restaurants):
    result = []
    for restaurant in restaurants:
        restaurant_dict = model_to_dict(restaurant)
        restaurant_dict["yelp_info"] = (
            get_restaurant_info_yelp_local(
                restaurant.business_id, restaurant.restaurant_name
            )
            if restaurant.business_id
            else None
        )

        if not restaurant_dict["yelp_info"]:
            restaurant_dict["yelp_info"] = default_info_page(restaurant.restaurant_name)

        latest_inspection_record = get_latest_inspection_record(
            restaurant.restaurant_name, restaurant.business_address, restaurant.postcode
        )
        restaurant_dict["latest_record"] = latest_inspection_record
        result.append(restaurant_dict)
    return result


def get_total_restaurant_number(
    keyword=None,
    neighbourhoods_filter=None,
    categories_filter=None,
    price_filter=None,
    rating_filter=None,
    compliant_filter=None,
    sort_option=None,
    favorite_filter=None,
    user=None,
):
    if (
        keyword
        or neighbourhoods_filter
        or categories_filter
        or price_filter
        or rating_filter
        or compliant_filter
        or sort_option
        or favorite_filter
    ):
        restaurants = get_filtered_restaurants(
            keyword,
            price_filter,
            neighbourhoods_filter,
            rating_filter,
            categories_filter,
            compliant_filter,
            0,
            None,
            None,
            favorite_filter,
            user,
        )
        return restaurants.count()

    return Restaurant.objects.filter(
        business_id__in=YelpRestaurantDetails.objects.all()
    ).count()


def get_restaurant_list(
    page,
    limit,
    keyword=None,
    neighbourhoods_filter=None,
    categories_filter=None,
    price_filter=None,
    rating_filter=None,
    compliant_filter=None,
    sort_option=None,
    favorite_filter=None,
    user=None,
):
    page = int(page) - 1
    offset = int(page) * int(limit)

    if (
        keyword
        or neighbourhoods_filter
        or categories_filter
        or price_filter
        or rating_filter
        or compliant_filter
        or sort_option
        or favorite_filter
    ):
        restaurants = get_filtered_restaurants(
            keyword,
            price_filter,
            neighbourhoods_filter,
            rating_filter,
            categories_filter,
            compliant_filter,
            page,
            limit,
            sort_option,
            favorite_filter,
            user,
        )
        return restaurants_to_dict(restaurants)
    else:
        restaurants = Restaurant.objects.filter(
            business_id__in=YelpRestaurantDetails.objects.all()
        )[
            offset : offset + int(limit)  # noqa: E203
        ]
        return restaurants_to_dict(restaurants)


def get_filtered_restaurants(
    keyword=None,
    price=None,
    neighborhood=None,
    rating=None,
    category=None,
    compliant=None,
    page=0,
    limit=None,
    sort_option=None,
    favorite_filter=None,
    user=None,
):
    filters = {}

    if not limit:
        limit = Restaurant.objects.all().count()

    offset = page * int(limit)
    if price:
        filters["price__in"] = price
    if neighborhood:
        filters["neighborhood__in"] = neighborhood
    if rating:
        filters["rating__in"] = rating
    if category:
        filters["category__parent_category__in"] = category

    keyword_filter = {}
    if keyword:
        keyword_filter["restaurant_name__icontains"] = keyword
    if compliant == "Compliant":
        keyword_filter["compliant_status__iexact"] = compliant

    value = None
    if sort_option:
        if sort_option == "ratedhigh":
            value = "-yelp_detail__rating"
        elif sort_option == "ratedlow":
            value = "yelp_detail__rating"
        elif sort_option == "pricehigh":
            value = "-yelp_detail__price"
        elif sort_option == "pricelow":
            value = "yelp_detail__price"
    if favorite_filter:
        if user.is_authenticated:
            if value:
                filtered_restaurants = user.favorite_restaurants.all()
                filtered_restaurants = (
                    filtered_restaurants.filter(
                        business_id__in=YelpRestaurantDetails.objects.filter(**filters)
                    )
                    .order_by(value)
                    .distinct()
                    .filter(**keyword_filter)[offset : offset + int(limit)]
                )
            else:
                filtered_restaurants = user.favorite_restaurants.all()
                filtered_restaurants = (
                    filtered_restaurants.filter(
                        business_id__in=YelpRestaurantDetails.objects.filter(**filters)
                    )
                    .distinct()
                    .filter(**keyword_filter)
                    .order_by("-id")[offset : offset + int(limit)]
                )

    elif value:
        filtered_restaurants = (
            Restaurant.objects.filter(
                business_id__in=YelpRestaurantDetails.objects.filter(**filters)
            )
            .order_by(value)
            .distinct()
            .filter(**keyword_filter)[offset : offset + int(limit)]
        )
    else:
        filtered_restaurants = (
            Restaurant.objects.filter(
                business_id__in=YelpRestaurantDetails.objects.filter(**filters)
            )
            .distinct()
            .filter(**keyword_filter)
            .order_by("-id")[offset : offset + int(limit)]
        )

    return filtered_restaurants


def get_latest_feedback(business_id):
    all_feedback_list = UserQuestionnaire.objects.filter(
        restaurant_business_id=business_id,
    ).order_by("-saved_on")
    if len(all_feedback_list) >= 1:
        latest_feedback = model_to_dict(all_feedback_list[0])
        return latest_feedback

    return None


def get_average_safety_rating(business_id):
    all_feedback_list = UserQuestionnaire.objects.filter(
        restaurant_business_id=business_id,
    )
    if len(all_feedback_list) >= 1:
        total = 0
        for feedback in all_feedback_list:
            total += int(feedback.safety_level)
        average_safety_rating = str(round(total / len(all_feedback_list), 2))
        return average_safety_rating
    return None


def get_csv_from_github():
    url = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/latest/last7days-by-modzcta.csv"  # noqa: E501
    download = requests.get(url).content
    return pd.read_csv(io.StringIO(download.decode("utf-8")))


def check_restaurant_saved(user, restaurant_id):
    return len(user.favorite_restaurants.all().filter(id=restaurant_id)) > 0
