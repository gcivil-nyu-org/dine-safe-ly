import requests
import json
import pandas as pd
from sodapy import Socrata
import csv
import numpy as np


def match_on_yelp(restaurant_name, restaurant_location):
    # parse location
    location_list = restaurant_location.split(", ")
    address1 = location_list[0]
    city = location_list[1]
    state = location_list[2]
    country = 'US'

    # Yelp API
    api_key = 'w5fGYpYDI6NYJOBI47KjmEJcROpCxq1VK841olTs0tSGOeGBNDuIIj8zF-C_MJFtAbrzfm7YF7bo72TxpOmrrn-zYnQ8xHBh_E4WEO39Z7IdKwbzCkBkCy0fjB6CX3Yx'
    headers = {'Authorization': 'Bearer %s' % api_key}
    # use business match endpoint
    url = 'https://api.yelp.com/v3/businesses/matches'
    params = {'name': restaurant_name, 'address1': address1, 'city': city, 'state': state, 'country': country}

    # making a get request to yelp api
    response = requests.get(url, params=params, headers=headers)
    return response.text.encode("utf8")


# Get open data as pandas dataframe
client = Socrata("data.cityofnewyork.us",
                 "dLBzJwg25psQttbxjLlQ8Z53V",
                 username="cx657@nyu.edu",
                 password="Dinesafely123")
results = client.get("4dx7-axux", limit=25000)
opendata_df = pd.DataFrame.from_records(results)
# print(opendata_df.columns)
grouped_opendata_df = opendata_df.groupby(['restaurantname','businessaddress'])
# print(len(grouped_opendata_df))
# for restaurant in grouped_opendata_df:
#     # print('\nCREATE TABLE {}('.format(restaurant))
#     print(restaurant[0][0])

with open('macthed_data.csv', 'w', encoding='utf-8', newline="") as matched_data_file:
    file_writer = csv.writer(matched_data_file)
    file_writer.writerow(['business_name', 'business_id', 'business_address'])

    for restaurant in grouped_opendata_df:
        # print('\nCREATE TABLE {}('.format(restaurant))
        # print(restaurant[0][0])
        restaurant_name = restaurant[0][0]
        restaurant_location = restaurant[0][1]
        # restaurant_zip_code = restaurant.iat[1,9]
        response = json.loads(match_on_yelp(restaurant_name, restaurant_location))

        if next(iter(response)) == 'error':
            # print("match failed")
            continue
        elif not response['businesses']:
            # print("no business info")
            continue
        else:
            # print(response)
            business_name=response['businesses'][0]['name']
            business_id = response['businesses'][0]['id']
            # print("The business {0} has business id as: {1}".format(business_name, business_id))
            file_writer.writerow([restaurant_name, business_id, restaurant_location])
    print("Done Matching")
    matched_data_file.close()
