

import pandas as pd
from sodapy import Socrata

from .models import Restaurant

def cleanInspectionData(results_df):
    restaurant_df = results_df.iloc[:,[0,1,2,3,4,9]]
    # print(restaurant_df)
    print(restaurant_df.shape)

    inspection_df = results_df.iloc[:,[5,6,7,8,10,1]]
    # print(inspection_df)
    print(inspection_df.shape)

    restaurant_df = restaurant_df.apply(lambda x: x.str.strip() if x.dtype == "str" else x)

    restaurant_df.drop_duplicates(subset=['restaurantname','legalbusinessname','postcode'], keep='last',inplace = True)
    print(restaurant_df.shape)
    return restaurant_df, inspection_df

# def saveRestaurants(restaurant_df):
#     for index, row in restaurant_df.iterrows():
#         # print(row['restaurantname'],row['businessaddress'],row['postcode'],row['legalbusinessname'],row['seatingchoice'],row['borough'])
#         r = Restaurant(restaurant_name=row['restaurantname'],business_address=row['businessaddress'],postcode=row['postcode'],legal_business_name=row['legalbusinessname'])
#         r.save()
#     return

def saveInspections(inspection_df):
    return


# client = Socrata("data.cityofnewyork.us", None)

client = Socrata("data.cityofnewyork.us",
                 "dLBzJwg25psQttbxjLlQ8Z53V",
                 username="cx657@nyu.edu",
                 password="Dinesafely123")

results = client.get("4dx7-axux",limit=25000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
print(results_df.shape)

restaurant_df, inspection_df = cleanInspectionData(results_df)

# saveRestaurants(restaurant_df)

saveInspections(inspection_df)