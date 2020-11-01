import os
import django
import requests
import json
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dinesafelysite.settings")
django.setup()

from restaurant.models import Zipcodes

logger = logging.getLogger(__name__)

def map_zipcode_to_neighbourhood():
    nyc_neigbourhoods_api = "https://data.beta.nyc/en/api/3/action/datastore_search?resource_id=7caac650-d082-4aea-9f9b-3681d568e8a5&limit=200"

    response = requests.get(nyc_neigbourhoods_api)
    data = json.loads(response.content)
    neighbourhood_data = data['result']['records']

    for zip in neighbourhood_data:
        try:
            neigbourhood_map = Zipcodes(zipcode = zip['zip'], borough = zip['borough'], neighborhood = zip['neighborhood'])
            neigbourhood_map.save()
        except Exception as e:
            logger.warning("Error while saving zipcode/neighbourhood to table Zipcodes: {}".format(zip['zip']))

if __name__ == "__main__":
    map_zipcode_to_neighbourhood()