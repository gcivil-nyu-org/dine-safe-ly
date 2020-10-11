# subjet to modify how to handle the output
# How it works:
# get name, location from opendata
# make a business match request to Yelp API
# get the unqiue business id from response
# Limited for the first 10 rows of opendata as exmaple due to possible limit of api calls

import requests
import json
import pandas as pd
from sodapy import Socrata
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
    # we are search for all restaurants in NYC
    params = {'name': restaurant_name, 'address1': address1, 'city': city, 'state': state, 'country': country}

    # making a get request to yelp api
    request = requests.get(url, params=params, headers=headers)
    # print(request)
    # proceed only if the status code is 200
    # print('The status code is {}'.format(request.status_code))

    # printing response
    # print(json.loads(request.text))
    return request.text


# Get open data as pandas dataframe
client = Socrata("data.cityofnewyork.us",
                 "dLBzJwg25psQttbxjLlQ8Z53V",
                 username="cx657@nyu.edu",
                 password="Dinesafely123")
results = client.get("4dx7-axux", limit=10)
opendata_df = pd.DataFrame.from_records(results)
# print(opendata_df)
address_list = {}

for i in range(len(opendata_df)):
    restaurant_name = opendata_df.iat[i, 1]
    restaurant_location = opendata_df.iat[i, 4]
    # print(restaurant_name)
    # print(restaurant_location)
    response = json.loads(match_on_yelp(restaurant_name, restaurant_location))
    # print("type of response is ", type(response))
    # print(response)
    business = response['businesses']
    # print("type of business is ", type(business))
    # print(business)
    if not business:
        print("match failed")
    else:
        business_name = response['businesses'][0]['name']
        business_id = response['businesses'][0]['id']
        print("The business {0} has business id as: {1}".format(business_name, business_id))
