import enum
from django.test import TestCase
from django.forms.models import model_to_dict
from django.urls import reverse

from .models import InspectionRecords, Restaurant
from unittest import mock
from .utils import *
import json


class Compliance(enum.Enum):
    no = "Non-Compliant"
    yes = "Compliant"
    skipped = "Skipped Inspection"


def create_restaurant(restaurant_name, business_address, postcode, business_id):
    return Restaurant.objects.create(restaurant_name=restaurant_name, business_address=business_address,
                                     postcode=postcode, business_id=business_id)


def create_inspection_records(restaurant_Inspection_ID, restaurant_name, postcode, business_address,
                              is_roadway_compliant, skipped_reason, inspected_on):
    if not isinstance(is_roadway_compliant, Compliance):
        raise TypeError('compliance_status must be an instance of Compliance enum')

    return InspectionRecords.objects.create(restaurant_Inspection_ID=restaurant_Inspection_ID,
                                            restaurant_name=restaurant_name, postcode=postcode,
                                            business_address=business_address,
                                            is_roadway_compliant=is_roadway_compliant,
                                            skipped_reason=skipped_reason, inspected_on=inspected_on)


class MockResponse():
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def content(self):
        return self.content

    def json(self):
        return self.content


class InspectionRecordsViewTests(TestCase):
    """ Tests for Inspection Record Views """

    def setUp(self):
        self.restaurant = create_restaurant(restaurant_name='Tacos El Paisa',
                                            business_address='1548 St. Nicholas btw West 187th street and west 188th '
                                                             'street, Manhattan, NY',
                                            postcode='10040', business_id='16')

    def tearDown(self):
        self.restaurant.delete()

    def test_get_valid_restaurant_inspections(self):
        response = self.client.get(reverse('restaurant:inspection_history', args=(self.restaurant.id,)))
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_restaurant_inspections(self):
        self.restaurant.id = -1
        response = self.client.get(reverse('restaurant:inspection_history', args=(self.restaurant.id,)))
        self.assertEqual(response.status_code, 404)




class RestaurantViewTests(TestCase):
    """ Test Restaurant Views """
    pass

class RestaurantUtilsTests(TestCase):
    def test_create_restaurant(self):
        restaurant = create_restaurant(restaurant_name='Gary Danko', business_address='800 N Point St', postcode='94109',
                                       business_id="WavvLdfdP6g8aZTtbBQHTw")
        self.assertIsNotNone(restaurant)
        self.assertEqual(restaurant.restaurant_name, 'Gary Danko')
        self.assertEqual(restaurant.business_address, '800 N Point St')
        self.assertEqual(restaurant.postcode, '94109')
        self.assertEqual(restaurant.business_id, 'WavvLdfdP6g8aZTtbBQHTw')
        self.assertEqual(str(restaurant), '1 Gary Danko 800 N Point St 94109 WavvLdfdP6g8aZTtbBQHTw')

    def test_merge_yelp_info(self):
        restaurant_info = MockResponse(json.dumps(
            {"id": "WavvLdfdP6g8aZTtbBQHTw",
             "name": "Gary Danko",
             "phone": "+14157492060", "display_phone": "(415) 749-2060", "review_count": 5296,
             "rating": 4.5,
             "price": "$$$$",
             }),200)
        restaurant_reviews = MockResponse(json.dumps({"reviews": [{"id": "xAG4O7l-t1ubbwVAlPnDKg", "rating": 5,
                                                                   "text": "Went back again to this place since the last time i visited the bay area 5 months ago, and nothing has changed. Still the sketchy Mission, Still the cashier...",
                                                                   "time_created": "2016-08-29 00:41:13"},
                                                                  {"id": "1JNmYjJXr9ZbsfZUAgkeXQ", "rating": 4,
                                                                   "text": "The \"restaurant\" is inside a small deli so there is no sit down area. Just grab and go.\n\nInside, they sell individually packaged ingredients so that you can...",
                                                                   "time_created": "2016-09-28 08:55:29"},
                                                                  {"id": "SIoiwwVRH6R2s2ipFfs4Ww", "rating": 4,
                                                                   "text": "Dear Mission District,\n\nI miss you and your many delicious late night food establishments and vibrant atmosphere.  I miss the way you sound and smell on a...",
                                                                   "time_created": "2016-08-10 07:56:44"}],
                                                      "total": 3, "possible_languages": ["en"]}), 200)
        self.assertEqual(merge_yelp_info(restaurant_info, restaurant_reviews),
                         {'info': json.loads(restaurant_info.content),
                          'reviews': json.loads(restaurant_reviews.content)})

    def test_get_restaurant_info_yelp(self):
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        response = get_restaurant_info_yelp(business_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["id"], business_id)

    def test_get_restaurant_reviews_yelp(self):
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        response = get_restaurant_reviews_yelp(business_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual("reviews" in data, True)

    @mock.patch("restaurant.utils.get_restaurant_info_yelp")
    @mock.patch("restaurant.utils.get_restaurant_reviews_yelp")
    def mock_query_yelp(self, mock_get_restaurant_info_yelp, mock_get_restaurant_reviews_yelp):
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        mock_get_restaurant_info_yelp.return_value = MockResponse({'id': business_id}, 200)
        mock_get_restaurant_reviews_yelp.return_value = MockResponse({'reviews': 1}, 200)
        data = query_yelp(business_id)
        self.assertIsNotNone(data)
        self.assertEqual(data, {'info': {'id': business_id}, 'reviews': {'reviews': 1}})


    @mock.patch("restaurant.models.Restaurant.objects.all")
    @mock.patch("restaurant.utils.get_latest_inspection_record")
    def test_get_restaurant_list(self, mock_objects, mock_get_latest_inspection_record):
        # mock_objects.return_value = [create_restaurant('Gary Danko', '800 N Point St', '94109', "WavvLdfdP6g8aZTtbBQHTw")]
        # print(mock_objects.return_value[0:1])
        # #mock_get_latest_inspection_record.return_value = model_to_dict(create_inspection_records('11157', 'Tacos El Paisa', '10040', '1548 St. Nicholas btw West 187th street and west 188th street, Manhattan, NY', Compliance.skipped, 'No Seating', '2020-07-16 18:09:42'))
        # #get_restaurant_list(0, 1)
        # TODO
        pass


class IntegratedInspectionRestaurantsTests(TestCase):
    """ Test Restaurant Views """
