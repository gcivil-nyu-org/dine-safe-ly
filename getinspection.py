

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dinesafelysite.settings')

import django
django.setup()
import pandas as pd
from sodapy import Socrata
import requests
import json

from restaurant.models import Restaurant, InspectionRecords
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

def match_on_yelp(restaurant_name, restaurant_location):
    location_list = restaurant_location.split(", ")
    address1 = location_list[0]
    city = location_list[1]
    state = location_list[2]
    country = 'US'

    api_key = 'JaekzvTTKsWGtQ96HUiwAXOUwRt6Ndbqzch4zc2XFnOEBxwTmwr-esm1uWo2QFvFJtXS8nY2dXx51cfAnMqVHpHRcp8N7QtP7LNVCcoxJWV_9NJrmZWSMiq-R_mEX3Yx'
    YELP_ACCESS_TOKE = 'A_V_V4rxelsvDsI2uFW1kT2mP2lUjd75GTEEsEcLnnvVOK5ssemrbw-R49czpANtS2ZtAeCl6FaapQrp1_30cRt9YKao3pFL1I6304sAtwKwKJkF1JBgF88FZl1_X3Yx'
    headers = {'Authorization': 'Bearer %s' % YELP_ACCESS_TOKE}
    url = 'https://api.yelp.com/v3/businesses/matches'
    params = {'name': restaurant_name, 'address1': address1, 'city': city, 'state': state, 'country': country}

    response = requests.get(url, params=params, headers=headers)
    return response.text.encode("utf8")

def clean_inspection_data(results_df):
    restaurant_df = results_df.loc[:,['restaurantname','legalbusinessname','businessaddress','postcode']]
    inspection_df = results_df.loc[:,['restaurantinspectionid','isroadwaycompliant','inspectedon','skippedreason','restaurantname','businessaddress','postcode']]

    restaurant_df = restaurant_df.apply(lambda x: x.str.strip() if x.dtype == "str" else x)

    restaurant_df.drop_duplicates(subset=['restaurantname','businessaddress','postcode'], keep='last',inplace = True)
    return restaurant_df, inspection_df

def save_restaurants(restaurant_df):
    for index, row in restaurant_df.iterrows():
        try:
            b_id = None
            response = json.loads(match_on_yelp(row['restaurantname'], row['businessaddress']))
            if next(iter(response)) == 'error':
                print("match failed")
                # print(response)
                continue
            elif not response['businesses']:
                print("not success")
                continue
            else:
                b_id = response['businesses'][0]['id']
                print("success")
                r = Restaurant(restaurant_name=row['restaurantname'],business_address=row['businessaddress'],postcode=row['postcode'],legal_business_name=row['legalbusinessname'],business_id=b_id)
                r.save()
        except:
            continue
    return

def save_inspections(inspection_df):
    for index, row in inspection_df.iterrows():
        try:
            # print(row)
            inspect_record = InspectionRecords(restaurant_name=row['restaurantname'],restaurant_Inspection_ID=row['restaurantinspectionid'],is_roadway_compliant=row['isroadwaycompliant'],business_address=row['businessaddress'],postcode=row['postcode'],skipped_reason=row['skippedreason'],inspected_on=row['inspectedon'])
            print(inspect_record)
            inspect_record.save()
        except Exception as e:
            print(e)
            # break
    return
import dateutil.parser

# if __name__ == '__main__':
@sched.scheduled_job('interval', minutes=2)
def get_inspection_data():
    # client = Socrata("data.cityofnewyork.us", None)
    #https://data.cityofnewyork.us/resource/4dx7-axux.json?$where=inspectedon > '2020-10-16T10:43:54.000'
    ir = InspectionRecords.objects.all().count()
    lastInspection = InspectionRecords.objects.order_by('-inspected_on')[0:1]
    # date = lastInspection.inspected_on
    # print(lastInspection[0].inspected_on)
    # a = dateutil.parser.parse(str(lastInspection[0].inspected_on)).date()
    date = str(lastInspection[0].inspected_on)
    print("check new date here")
    print(date)
    date = date.replace(" ",'T')
    var = 'inspectedon > \''+ date + '\''
    # print(a)

    client = Socrata("data.cityofnewyork.us",
                    "dLBzJwg25psQttbxjLlQ8Z53V",
                    username="cx657@nyu.edu",
                    password="Dinesafely123")

    results = client.get("4dx7-axux",where = var)
    # print(results)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    # print(results_df)
    restaurant_df, inspection_df = clean_inspection_data(results_df)
    save_restaurants(restaurant_df)

    save_inspections(inspection_df)

# if __name__ == '__main__':
#     get_inspection_data()
sched.start()
print("scheduler started")