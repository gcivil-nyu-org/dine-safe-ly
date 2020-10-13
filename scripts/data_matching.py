import requests
import json
import pandas as pd
from sodapy import Socrata
import csv


def match_on_yelp(restaurant_name, restaurant_location):
    location_list = restaurant_location.split(", ")
    address1 = location_list[0]
    city = location_list[1]
    state = location_list[2]
    country = 'US'

    api_key = 'JaekzvTTKsWGtQ96HUiwAXOUwRt6Ndbqzch4zc2XFnOEBxwTmwr-esm1uWo2QFvFJtXS8nY2dXx51cfAnMqVHpHRcp8N7QtP7LNVCcoxJWV_9NJrmZWSMiq-R_mEX3Yx'
    headers = {'Authorization': 'Bearer %s' % api_key}
    url = 'https://api.yelp.com/v3/businesses/matches'
    params = {'name': restaurant_name, 'address1': address1, 'city': city, 'state': state, 'country': country}

    response = requests.get(url, params=params, headers=headers)
    return response.text.encode("utf8")


if __name__ == '__main__':
    client = Socrata("data.cityofnewyork.us",
                     "dLBzJwg25psQttbxjLlQ8Z53V",
                     username="cx657@nyu.edu",
                     password="Dinesafely123")
    results = client.get("4dx7-axux", limit=25)
    opendata_df = pd.DataFrame.from_records(results)

    grouped_opendata_df = opendata_df.groupby(['restaurantname', 'businessaddress'])

    with open('matched_data.csv', 'w', encoding='utf-8', newline="") as matched_data_file:
        file_writer = csv.writer(matched_data_file)
        file_writer.writerow(['business_name', 'business_id', 'business_address'])
        for restaurant in grouped_opendata_df:
            restaurant_name = restaurant[0][0]
            restaurant_location = restaurant[0][1]
            response = json.loads(match_on_yelp(restaurant_name, restaurant_location))
            if next(iter(response)) == 'error':
                # print("match failed")
                continue
            elif not response['businesses']:
                # print("no business info")
                continue
            else:
                business_name = response['businesses'][0]['name']
                business_id = response['businesses'][0]['id']
                file_writer.writerow([restaurant_name, business_id, restaurant_location])
        print("Done Matching")
        matched_data_file.close()
