import os
import django

import pandas as pd
from sodapy import Socrata

import requests
import json

# from apscheduler.schedulers.blocking import BlockingScheduler

# import dateutil.parser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dinesafelysite.settings")
django.setup()

from restaurant.models import Restaurant, InspectionRecords  # noqa: E402


# sched = BlockingScheduler()


def match_on_yelp(restaurant_name, restaurant_location):
    location_list = restaurant_location.split(", ")
    address1 = location_list[0]
    city = "New York"
    state = "NY"
    country = "US"

    # YELP_ACCESS_TOKE = (
    #     "JaekzvTTKsWGtQ96HUiwAXOUwRt6Ndbqzch4zc2XFnOEBxwTmwr"
    #     "-esm1uWo2QFvFJtXS8nY2dXx51cfAnMqVHpHRcp8N7QtP7LNVCcoxJWV_9NJrmZWSMiq"
    #     "-R_mEX3Yx "
    # )
    YELP_ACCESS_TOKE = (
        "A_V_V4rxelsvDsI2uFW1kT2mP2lUjd75GTEEsEcLnnvVOK5ssemrbw"
        "-R49czpANtS2ZtAeCl6FaapQrp1_30cRt9YKao3pFL1I6304sAtwKwKJk"
        "F1JBgF88FZl1_X3Yx "
    )
    headers = {"Authorization": "Bearer %s" % YELP_ACCESS_TOKE}
    url = "https://api.yelp.com/v3/businesses/matches"
    params = {
        "name": restaurant_name,
        "address1": address1,
        "city": city,
        "state": state,
        "country": country,
    }

    response = requests.get(url, params=params, headers=headers)
    return response.text.encode("utf8")


def clean_inspection_data(results_df):
    restaurant_df = results_df.loc[:, ["restaurantname", "businessaddress", "postcode"]]
    inspection_df = results_df.loc[
        :,
        [
            "restaurantinspectionid",
            "isroadwaycompliant",
            "inspectedon",
            "skippedreason",
            "restaurantname",
            "businessaddress",
            "postcode",
        ],
    ]
    restaurant_df = restaurant_df.apply(
        lambda x: x.str.strip() if x.dtype == "str" else x
    )

    restaurant_df = restaurant_df[restaurant_df["restaurantname"] != "Test"]
    restaurant_df = restaurant_df[restaurant_df["restaurantname"] != "test"]
    restaurant_df = restaurant_df[restaurant_df["restaurantname"] != "TEST"]

    restaurant_df.drop_duplicates(
        subset=["restaurantname", "businessaddress", "postcode"],
        keep="last",
        inplace=True,
    )
    return restaurant_df, inspection_df


def save_restaurants(restaurant_df):
    for index, row in restaurant_df.iterrows():
        try:
            response = json.loads(
                match_on_yelp(row["restaurantname"], row["businessaddress"])
            )
            if next(iter(response)) == "error":
                continue
            elif not response["businesses"]:
                continue
            # else:
            #     b_id = response["businesses"][0]["id"]

            # r = Restaurant(
            #     restaurant_name=row["restaurantname"],
            #     business_address=row["businessaddress"],
            #     postcode=row["postcode"],
            #     # legal_business_name=row["legalbusinessname"],
            #     # business_id=b_id,
            # )
            # r.save()
        except OSError:
            print("save_restaurant failed")
            raise
    return


def save_inspections(inspection_df):
    for index, row in inspection_df.iterrows():
        try:

            inspect_record = InspectionRecords(
                restaurant_name=row["restaurantname"],
                restaurant_inspection_id=row["restaurantinspectionid"],
                is_roadway_compliant=row["isroadwaycompliant"],
                business_address=row["businessaddress"],
                postcode=row["postcode"],
                skipped_reason=row["skippedreason"],
                inspected_on=row["inspectedon"],
            )
            inspect_record.save()

        except Exception as e:
            print(e)
    return


# @sched.scheduled_job("interval", minutes=1)
def get_inspection_data():
    # ir = InspectionRecords.objects.all().count()
    # lastInspection = InspectionRecords.objects.order_by("-inspected_on")[0:1]
    # date = str(lastInspection[0].inspected_on)
    # print(date)
    # date = date.replace(" ", "T")
    # date_query = "inspectedon > '" + date + "'"

    client = Socrata(
        "data.cityofnewyork.us",
        "dLBzJwg25psQttbxjLlQ8Z53V",
        username="cx657@nyu.edu",
        password="Dinesafely123",
    )

    # results = client.get("4dx7-axux", where=date_query)
    results = client.get("4dx7-axux", limit=30000)

    # Convert to pandas DataFrame

    results_df = pd.DataFrame.from_records(results)
    # results_df = pd.read_csv('/Users/xiechenwei/Downloads/opendata_restaurant.csv')
    print(results_df.shape)
    print(results_df.columns)

    if results_df.shape[0] > 0:
        restaurant_df, inspection_df = clean_inspection_data(results_df)
        save_restaurants(restaurant_df)
        # print(inspection_df)
        save_inspections(inspection_df)


# sched.start()


def populate_restaurant_with_yelp_id():
    restaurants = Restaurant.objects.all()[4316:6849]
    limit = 3000
    count = 0
    for r in restaurants:
        if r.business_id:
            count += 1
            continue

        response = json.loads(match_on_yelp(r.restaurant_name, r.business_address))

        if next(iter(response)) == "error":
            continue
        elif not response["businesses"]:
            continue
        else:
            b_id = response["businesses"][0]["id"]
        r.business_id = b_id
        r.save()
        count += 1
        limit -= 1
        if limit == 0:
            break
    print(count)


if __name__ == "__main__":
    populate_restaurant_with_yelp_id()
    # get_inspection_data()
