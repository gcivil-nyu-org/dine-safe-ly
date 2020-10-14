

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dinesafelysite.settings')

import django
django.setup()
import pandas as pd
from sodapy import Socrata

from restaurant.models import Restaurant, InspectionRecords

def clean_inspection_data(results_df):
    restaurant_df = results_df.loc[:,['restaurantname','legalbusinessname','businessaddress','postcode']]
    inspection_df = results_df.loc[:,['restaurantinspectionid','isroadwaycompliant','inspectedon','skippedreason','restaurantname','businessaddress','postcode']]

    restaurant_df = restaurant_df.apply(lambda x: x.str.strip() if x.dtype == "str" else x)

    restaurant_df.drop_duplicates(subset=['restaurantname','businessaddress','postcode'], keep='last',inplace = True)
    return restaurant_df, inspection_df

def save_restaurants(restaurant_df):
    for index, row in restaurant_df.iterrows():
        try:
            r = Restaurant(restaurant_name=row['restaurantname'],business_address=row['businessaddress'],postcode=row['postcode'],legal_business_name=row['legalbusinessname'])
            r.save()
        except:
            continue
    return

def save_inspections(inspection_df):
    for index, row in inspection_df.iterrows():
        try:
            # print(row)
            inspect_record = InspectionRecords(restaurant_name=row['restaurantname'],restaurant_Inspection_ID=row['restaurantinspectionid'],is_roadway_compliant=row['isroadwaycompliant'],business_address=row['businessaddress'],postcode=row['postcode'],skipped_reason=row['skippedreason'],inspected_on=row['inspectedon'])
            # print(inspect_record)
            inspect_record.save()
        except Exception as e:
            print(e)
            # break
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
    restaurant_df, inspection_df = clean_inspection_data(results_df)
    save_restaurants(restaurant_df)

    save_inspections(inspection_df)


