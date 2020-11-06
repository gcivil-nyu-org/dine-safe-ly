import os
import django
import requests
import json
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dinesafelysite.settings")
django.setup()

from django.conf import settings
from restaurant.models import Zipcodes, YelpRestaurantDetails, Restaurant
from restaurant.utils import query_yelp

logger = logging.getLogger(__name__)


def map_zipcode_to_neighbourhood():
    nyc_neigbourhoods_api = "https://data.beta.nyc/en/api/3/action/datastore_search?resource_id=7caac650-d082-4aea-9f9b-3681d568e8a5&limit=200"

    response = requests.get(nyc_neigbourhoods_api)
    data = json.loads(response.content)
    neighbourhood_data = data["result"]["records"]

    for zip in neighbourhood_data:
        try:
            neigbourhood_map = Zipcodes(
                zipcode=zip["zip"],
                borough=zip["borough"],
                neighborhood=zip["neighborhood"],
            )
            neigbourhood_map.save()
        except Exception as e:
            logger.warning(
                "Error while saving zipcode/neighbourhood to table Zipcodes: {} {}".format(
                    zip["zip"], e
                )
            )


def get_neighbourhood(zip):
    area = Zipcodes.objects.get(zipcode=zip)
    return area.neighborhood


def get_restaurant_category_yelp(alias):
    access_token = settings.YELP_ACESS_TOKEN_BETA
    headers = {"Authorization": "bearer %s" % access_token}
    url = settings.YELP_CATEGORY_API + alias
    response = requests.get(url, headers=headers)
    return json.loads(response.content)


def get_cuisine(categories):

    for c in categories:
        category = get_restaurant_category_yelp(c["alias"])
        if (
            not category["category"]["parent_aliases"]
            or category["category"]["parent_aliases"][0] == "restaurants"
        ):
            return c["alias"]
        else:
            return category["category"]["parent_aliases"][0]


def validate_fields(restaurant_info):
    keys = [
        "neighborhood",
        "category",
        "price",
        "rating",
        "latitude",
        "longitude",
        "img_url",
    ]
    restaurant_data = dict.fromkeys(keys)

    if "info" in restaurant_info.keys():
        if "price" in restaurant_info["info"].keys():
            restaurant_data["price"] = restaurant_info["info"]["price"]
        if "rating" in restaurant_info["info"].keys():
            restaurant_data["rating"] = restaurant_info["info"]["rating"]
        if "image_url" in restaurant_info["info"].keys():
            restaurant_data["img_url"] = restaurant_info["info"]["image_url"]
        if "coordinates" in restaurant_info["info"].keys():
            if "latitude" in restaurant_info["info"]["coordinates"].keys():
                restaurant_data["latitude"] = restaurant_info["info"]["coordinates"][
                    "latitude"
                ]
            if "latitude" in restaurant_info["info"]["coordinates"].keys():
                restaurant_data["longitude"] = restaurant_info["info"]["coordinates"][
                    "longitude"
                ]
        if "location" in restaurant_info["info"].keys():
            if "zip_code" in restaurant_info["info"]["location"].keys():
                restaurant_data["neighborhood"] = get_neighbourhood(
                    restaurant_info["info"]["location"]["zip_code"]
                )
        if "categories" in restaurant_info["info"].keys():
            restaurant_data["category"] = get_cuisine(
                restaurant_info["info"]["categories"]
            )

    return restaurant_data


def save_yelp_restaurant_details():

    for r in Restaurant.objects.all():
        try:
            if r.business_id:
                restaurant_info = query_yelp(r.business_id)

                restaurant_data = validate_fields(restaurant_info)

                details = YelpRestaurantDetails(
                    business_id=r.business_id,
                    neighborhood=restaurant_data["neighborhood"],
                    category=restaurant_data["category"],
                    price=restaurant_data["price"],
                    rating=restaurant_data["rating"],
                    img_url=restaurant_data["img_url"],
                    latitude=restaurant_data["latitude"],
                    longitude=restaurant_data["longitude"],
                )

                details.save()

                logger.info(
                    "Yelp restaurant details successfully saved: {}".format(
                        r.business_id
                    )
                )
            else:
                continue
        except Exception as e:
            logger.error(
                "Error while saving to table YelpRestaurantDetails: {} {}".format(
                    r.business_id, e
                )
            )


if __name__ == "__main__":
    # map_zipcode_to_neighbourhood()
    save_yelp_restaurant_details()
