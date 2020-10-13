

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dinesafelysite.settings')

import django
django.setup()
import pandas as pd
from sodapy import Socrata

from restaurant.models import Restaurant, InspectionRecords

def cleanInspectionData(results_df):
    restaurant_df = results_df.iloc[:,[0,1,2,3,4,9]]
    inspection_df = results_df.iloc[:,[5,6,7,8,10,1]]

    restaurant_df = restaurant_df.apply(lambda x: x.str.strip() if x.dtype == "str" else x)

    restaurant_df.drop_duplicates(subset=['restaurantname','businessaddress','postcode'], keep='last',inplace = True)
    return restaurant_df, inspection_df

def saveRestaurants(restaurant_df):
    for index, row in restaurant_df.iterrows():
        try:
            r = Restaurant(restaurant_name=row['restaurantname'],business_address=row['businessaddress'],postcode=row['postcode'],legal_business_name=row['legalbusinessname'])
            r.save()
        except:
            continue
    return

def saveInspections(inspection_df):
    for index, row in inspection_df.iterrows():
        try:
            inspectRecord = InspectionRecords(restaurant_name=row['restaurantname'],restaurant_Inspection_ID=row['restaurantinspectionid'],is_roadway_compliant=row['isroadwaycompliant'],skipped_reason=row['skippedreason'],inspected_on=row['inspectedon'])
            inspectRecord.save()
        except:
            continue
    return

if __name__ == '__main__':
    # client = Socrata("data.cityofnewyork.us", None)

    client = Socrata("data.cityofnewyork.us",
                    "dLBzJwg25psQttbxjLlQ8Z53V",
                    username="cx657@nyu.edu",
                    password="Dinesafely123")

    results = client.get("4dx7-axux",limit=25000)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    restaurant_df, inspection_df = cleanInspectionData(results_df)
    saveRestaurants(restaurant_df)

    saveInspections(inspection_df)


