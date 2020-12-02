import os
import django
import requests
import json
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dinesafelysite.settings")
django.setup()

from django.conf import settings
from restaurant.models import (
    Zipcodes,
    YelpRestaurantDetails,
    Categories,
    Restaurant,
    InspectionRecords,
)
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


def save_yelp_categories():
    access_token = settings.YELP_ACCESS_TOKEN_CATEGORY
    headers = {"Authorization": "bearer %s" % access_token}
    url = settings.YELP_CATEGORY_API
    response = requests.get(url, headers=headers)
    categories = json.loads(response.content)

    for c in categories["categories"]:
        try:
            alias = c["alias"]
            parent = None

            if c["parent_aliases"] and c["parent_aliases"][0] == "restaurants":
                parent = alias
            elif c["parent_aliases"]:
                parent = c["parent_aliases"][0]

            cat = Categories(category=alias, parent_category=parent)
            cat.save()
            print(alias, parent)
        except Exception as e:
            logger.error("Error while getting categories for  Restaurant: {}".format(e))

            continue


def get_neighbourhood(zip):
    area = Zipcodes.objects.get(zipcode=zip)
    if area:
        return area.neighborhood
    else:
        return None


def get_restaurant_category_yelp(alias):
    access_token = settings.YELP_ACCESS_TOKEN_CATEGORY
    headers = {"Authorization": "bearer %s" % access_token}
    url = settings.YELP_CATEGORY_API + alias
    response = requests.get(url, headers=headers)
    return json.loads(response.content)


def get_cuisine(categories):
    cuisines = list()
    for c in categories:
        # category = get_restaurant_category_yelp(c["alias"])
        # if (
        #     not category["category"]["parent_aliases"]
        #     or category["category"]["parent_aliases"][0] == "restaurants"
        # ):
        #     return c["alias"]
        # else:
        #     return category["category"]["parent_aliases"][0]
        cuisine = Categories.objects.get(category=c["alias"])
        # print(cuisine)
        cuisines.append(cuisine)
    return cuisines


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


def save_yelp_restaurant_details(business_id):

    # for r in Restaurant.objects.all():
    try:
        if business_id:
            restaurant_info = query_yelp(business_id)

            restaurant_data = validate_fields(restaurant_info)

            details = YelpRestaurantDetails(
                business_id=business_id,
                neighborhood=restaurant_data["neighborhood"],
                # category=restaurant_data["category"],
                price=restaurant_data["price"],
                rating=restaurant_data["rating"],
                img_url=restaurant_data["img_url"],
                latitude=restaurant_data["latitude"],
                longitude=restaurant_data["longitude"],
            )

            # print(details)
            details.save()
            for cat in restaurant_data["category"]:
                # print(cat)
                details.category.add(cat)
                details.save()

            logger.info(
                "Yelp restaurant details successfully saved: {}".format(business_id)
            )
            return details
    except Exception as e:
        logger.error(
            "Error while saving to table YelpRestaurantDetails: {} {}".format(
                business_id, e
            )
        )


def update_restuarant_inspection(restaurant):
    if restaurant.business_id:
        record = InspectionRecords.objects.filter(
            business_id=restaurant.business_id
        ).order_by("-inspected_on")[0:1]
        if record:
            Restaurant.objects.filter(business_id=restaurant.business_id).update(
                compliant_status=record[0].is_roadway_compliant
            )

            logger.info(
                "Compliance updated: {}  {}".format(
                    restaurant.business_id, record[0].is_roadway_compliant
                )
            )

    else:
        record = InspectionRecords.objects.filter(
            restaurant_name=restaurant.restaurant_name,
            business_address=restaurant.business_address,
            postcode=restaurant.postcode,
        ).order_by("-inspected_on")[0:1]

        if record:
            Restaurant.objects.filter(
                restaurant_name=restaurant.restaurant_name,
                business_address=restaurant.business_address,
                postcode=restaurant.postcode,
            ).update(compliant_status=record[0].is_roadway_compliant)

            logger.info(
                "Compliance updated: {}  {}".format(
                    restaurant.restaurant_name, record[0].is_roadway_compliant
                )
            )


if __name__ == "__main__":
    # map_zipcode_to_neighbourhood()
    # save_yelp_restaurant_details()
    save_yelp_categories()
    # save_yelp_restaurant_details("-7PnG_cD9VY-IfHGWzynmQ")

    # restaurants = Restaurant.objects.all()[2400:]
    # for r in restaurants:
    #     update_restuarant_inspection(r)
