from django.test import RequestFactory, TestCase
from django.forms.models import model_to_dict
from django.test import Client
from datetime import datetime, timedelta
from unittest import mock
from .forms import QuestionnaireForm
from .models import (
    Restaurant,
    InspectionRecords,
    YelpRestaurantDetails,
    Zipcodes,
    UserQuestionnaire,
    Categories,
)
from .views import get_inspection_info, get_landing_page, get_restaurant_profile
from .utils import (
    merge_yelp_info,
    get_restaurant_info_yelp,
    get_restaurant_reviews_yelp,
    query_yelp,
    get_latest_inspection_record,
    get_restaurant_list,
    get_filtered_restaurants,
    get_latest_feedback,
    get_average_safety_rating,
)

# from getinspection import (
#     clean_inspection_data,
#     match_on_yelp,
#     save_restaurants,
#     save_inspections,
# )
# import pandas as pd
import json


# from pandas.util.testing import assert_frame_equal


def create_restaurant(restaurant_name, business_address, postcode, business_id):
    return Restaurant.objects.create(
        restaurant_name=restaurant_name,
        business_address=business_address,
        postcode=postcode,
        business_id=business_id,
    )


def create_inspection_records(
    restaurant_inspection_id,
    restaurant_name,
    postcode,
    business_address,
    is_roadway_compliant,
    skipped_reason,
    inspected_on,
    business_id=None,
):
    return InspectionRecords.objects.create(
        restaurant_inspection_id=restaurant_inspection_id,
        restaurant_name=restaurant_name,
        postcode=postcode,
        business_address=business_address,
        is_roadway_compliant=is_roadway_compliant,
        skipped_reason=skipped_reason,
        inspected_on=inspected_on,
        business_id=business_id,
    )


def create_yelp_restaurant_details(
    business_id, neighborhood, price, rating, img_url, latitude, longitude
):
    return YelpRestaurantDetails.objects.create(
        business_id=business_id,
        neighborhood=neighborhood,
        price=price,
        rating=rating,
        img_url=img_url,
        latitude=latitude,
        longitude=longitude,
    )


class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def content(self):
        return self.content


class ModelTests(TestCase):
    def test_create_restaurant(self):
        restaurant = create_restaurant(
            restaurant_name="Gary Danko",
            business_address="800 N Point St",
            postcode="94109",
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        self.assertIsNotNone(restaurant)
        self.assertEqual(restaurant.restaurant_name, "Gary Danko")
        self.assertEqual(restaurant.business_address, "800 N Point St")
        self.assertEqual(restaurant.postcode, "94109")
        self.assertEqual(restaurant.business_id, "WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(
            str(restaurant),
            "1 Gary Danko 800 N Point St 94109 WavvLdfdP6g8aZTtbBQHTw None",
        )

    def test_create_categories(self):
        cat = Categories(category="wine_bar", parent_category="bars")
        self.assertIsNotNone(cat)
        self.assertEqual(cat.category, "wine_bar")

    def test_create_inspection_records(self):
        inspection_record = create_inspection_records(
            restaurant_inspection_id="27555",
            restaurant_name="blah blah",
            postcode="11101",
            business_address="somewhere in LIC",
            is_roadway_compliant="Compliant",
            skipped_reason="Nan",
            inspected_on=datetime(2020, 10, 24, 17, 36),
        )
        self.assertIsNotNone(inspection_record)
        self.assertEqual(inspection_record.restaurant_inspection_id, "27555")
        self.assertEqual(inspection_record.restaurant_name, "blah blah")
        self.assertEqual(inspection_record.postcode, "11101")
        self.assertEqual(inspection_record.business_address, "somewhere in LIC")
        self.assertEqual(inspection_record.is_roadway_compliant, "Compliant")
        self.assertEqual(inspection_record.skipped_reason, "Nan")
        self.assertEqual(inspection_record.inspected_on, datetime(2020, 10, 24, 17, 36))
        self.assertEqual(
            str(inspection_record),
            "27555 blah blah Compliant Nan 2020-10-24 17:36:00 "
            "11101 somewhere in LIC None",
        )

    def test_yelp_restaurant_details(self):
        Categories.objects.create(category="wine_bar", parent_category="bars")
        details = YelpRestaurantDetails.objects.create(
            business_id="WavvLdfdP6g8aZTtbBQHTw",
            neighborhood="Upper East Side",
            price="$$",
            rating=4.0,
            img_url="https://s3-media1.fl.yelpcdn.com/bphoto/C4emY32GDusdMCybR6NmpQ/o.jpg",
            latitude=40.8522129,
            longitude=-73.8290069,
        )
        category = Categories.objects.get(category="wine_bar")
        details.category.add(category)
        self.assertIsNotNone(details)
        self.assertEqual(details.business_id, "WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(details.neighborhood, "Upper East Side")
        self.assertEqual(details.price, "$$")
        self.assertEqual(details.rating, 4.0)
        self.assertEqual(
            details.img_url,
            "https://s3-media1.fl.yelpcdn.com/bphoto/C4emY32GDusdMCybR6NmpQ/o.jpg",
        )
        self.assertEqual(details.latitude, 40.8522129)
        self.assertEqual(details.longitude, -73.8290069)
        self.assertEqual(
            str(details),
            "WavvLdfdP6g8aZTtbBQHTw Upper East Side restaurant.Categories.None $$ 4.0 https://s3-media1.fl.yelpcdn.com/bphoto/C4emY32GDusdMCybR6NmpQ/o.jpg 40.8522129 -73.8290069",
        )

    def test_create_zipcodes(self):
        neigbourhood_map = Zipcodes(
            zipcode="11220",
            borough="Brooklyn",
            neighborhood="Sunset Park",
        )

        self.assertIsNotNone(neigbourhood_map)
        self.assertEqual(neigbourhood_map.zipcode, "11220")
        self.assertEqual(neigbourhood_map.borough, "Brooklyn")
        self.assertEqual(neigbourhood_map.neighborhood, "Sunset Park")
        self.assertEqual(str(neigbourhood_map), "11220 Brooklyn Sunset Park")

    def test_create_questionnaire(self):
        questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        self.assertIsNotNone(questionnaire)
        self.assertEqual(questionnaire.restaurant_business_id, "WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(questionnaire.user_id, "1")
        self.assertEqual(questionnaire.safety_level, "5")
        self.assertIsNotNone(questionnaire.saved_on)
        self.assertEqual(questionnaire.temperature_required, "True")
        self.assertEqual(questionnaire.contact_info_required, "True")
        self.assertEqual(questionnaire.employee_mask, "True")
        self.assertEqual(questionnaire.capacity_compliant, "True")
        self.assertEqual(questionnaire.distance_compliant, "True")
        self.assertEqual(
            str(questionnaire),
            "WavvLdfdP6g8aZTtbBQHTw 1 5 "
            + str(questionnaire.saved_on)
            + " True True True True True",
        )


class InspectionRecordsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.inspection_records = create_inspection_records(
            restaurant_inspection_id="24111",
            restaurant_name="Tacos El Paisa",
            postcode="10040",
            business_address="1548 St. Nicholas btw West 187th street "
            "and west 188th "
            "street, Manhattan, NY",
            is_roadway_compliant="Compliance",
            skipped_reason="No Seating",
            inspected_on=datetime(2020, 10, 21, 12, 30, 30),
        )
        self.restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            postcode="10040",
            business_id="16",
        )

    def test_get_valid_restaurant_inspections(self):
        request = self.factory.get("restaurant:inspection_history")
        request.restaurant = self.restaurant
        response = get_inspection_info(request, self.restaurant.id)
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_restaurant_inspections(self):
        request = self.factory.get("restaurant:inspection_history")
        request.restaurant = self.restaurant
        self.restaurant.id = -1
        response = get_inspection_info(request, self.restaurant.id)
        self.assertEqual(response.status_code, 404)


class BaseTest(TestCase):
    def setUp(self):
        self.user_register_url = "user:register"
        self.c = Client()
        self.dummy_user_questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )

        return super().setUp


class UserQuestionnaireFormTests(BaseTest):
    def test_no_business_id(self):
        self.form_no_business_id = {
            "restaurant_business_id": "",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_business_id)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_user_id(self):
        self.form_no_user_id = {
            "restaurant_business_id": "",
            "user_id": "",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_user_id)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_safety_level(self):
        self.form_no_safety_level = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_safety_level)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_temperature_required(self):
        self.form_no_temperature_required = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_temperature_required)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_contact_info_required(self):
        self.form_no_contact_info_required = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_contact_info_required)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_employee_mask(self):
        self.form_no_employee_mask = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_employee_mask)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_capacity_compliant(self):
        self.form_no_capacity_compliant = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "",
            "distance_compliant": "True",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_capacity_compliant)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_distance_compliant(self):
        self.form_no_distance_compliant = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_distance_compliant)
        self.assertFalse(questionnaire_form.is_valid())

    def test_form_valid(self):
        self.form_valid = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "safety_level": "5",
            "saved_on": datetime.now(),
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        form = QuestionnaireForm(self.form_valid)
        self.assertTrue(form.is_valid())

    def test_form_submission(self):
        print("in test_form_submission")
        create_restaurant(
            "random_name",
            "random_address",
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        print(Restaurant.objects.all()[0])
        self.form = {
            "restaurant_business_id": "U8C69ISrhGTTubjqoVgZYg",
            "user_id": "1",
            "safety_level": "5",
            "saved_on": datetime.now(),
            "temperature_required": "True",
            "contact_info_required": "True",
            "employee_mask": "True",
            "capacity_compliant": "True",
            "distance_compliant": "True",
        }
        form = QuestionnaireForm(self.form)
        response = self.c.post("/restaurant/profile/1/", self.form)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 200)


class SearchFilterFormTests(BaseTest):
    def test_search_filter(self):
        search_filter_form = {
            "keyword": "chicken",
            "neighbourhood": ["Chelsea and Clinton"],
            "category": ["korean"],
            "price_1": True,
            "price_2": True,
            "price_3": True,
            "price_4": True,
            "rating": [1, 2, 3],
            "All": "Compliant",
        }
        response = self.c.post(
            "/restaurant/search_filter/restaurants_list/1", search_filter_form
        )
        self.assertEqual(response.status_code, 200)


class RestaurantViewTests(TestCase):
    """ Test Restaurant Views """

    def setUp(self):
        self.factory = RequestFactory()
        self.restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            postcode="10040",
            business_id="16",
        )

    def test_get_valid_restaurant_profile(self):
        request = self.factory.get("restaurant:profile")
        request.restaurant = self.restaurant
        response = get_restaurant_profile(request, self.restaurant.id)
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_restaurant_profile(self):
        request = self.factory.get("restaurant:profile")
        request.restaurant = self.restaurant
        self.restaurant.id = -1
        response = get_restaurant_profile(request, self.restaurant.id)
        self.assertEqual(response.status_code, 404)

    def test_valid_get_landing_page(self):
        request = self.factory.get("restaurant:browse")
        response = get_landing_page(request, 6)
        self.assertEqual(response.status_code, 200)


class RestaurantUtilsTests(TestCase):
    def test_merge_yelp_info(self):
        restaurant_info = MockResponse(
            json.dumps(
                {
                    "id": "WavvLdfdP6g8aZTtbBQHTw",
                    "name": "Gary Danko",
                    "phone": "+14157492060",
                    "display_phone": "(415) 749-2060",
                    "review_count": 5296,
                    "rating": 4.5,
                    "price": "$$$$",
                }
            ),
            200,
        )
        restaurant_reviews = MockResponse(
            json.dumps(
                {
                    "reviews": [
                        {
                            "id": "xAG4O7l-t1ubbwVAlPnDKg",
                            "rating": 5,
                            "text": "Went back again to this place since the last "
                            "time i visited the bay area 5 "
                            "months ago, and nothing has changed. Still the "
                            "sketchy Mission, "
                            "Still the cashier...",
                            "time_created": "2016-08-29 00:41:13",
                        },
                        {
                            "id": "1JNmYjJXr9ZbsfZUAgkeXQ",
                            "rating": 4,
                            "text": 'The "restaurant" is inside a small deli so there '
                            "is no sit down area. Just grab "
                            "and go.\n\nInside, they sell individually "
                            "packaged ingredients so that you "
                            "can...",
                            "time_created": "2016-09-28 08:55:29",
                        },
                        {
                            "id": "SIoiwwVRH6R2s2ipFfs4Ww",
                            "rating": 4,
                            "text": "Dear Mission District,\n\nI miss you and your "
                            "many delicious late night food "
                            "establishments and vibrant atmosphere.  I miss "
                            "the way you sound and smell on "
                            "a...",
                            "time_created": "2016-08-10 07:56:44",
                        },
                    ],
                    "total": 3,
                    "possible_languages": ["en"],
                }
            ),
            200,
        )
        self.assertEqual(
            merge_yelp_info(restaurant_info, restaurant_reviews),
            {
                "info": json.loads(restaurant_info.content),
                "reviews": json.loads(restaurant_reviews.content),
            },
        )

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

    @mock.patch("restaurant.utils.get_restaurant_reviews_yelp")
    @mock.patch("restaurant.utils.get_restaurant_info_yelp")
    def test_query_yelp(
        self, mock_get_restaurant_info_yelp, mock_get_restaurant_reviews_yelp
    ):
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        mock_get_restaurant_info_yelp.return_value = MockResponse(
            json.dumps({"id": business_id}), 200
        )
        mock_get_restaurant_reviews_yelp.return_value = MockResponse(
            json.dumps({"reviews": 1}), 200
        )
        data = query_yelp(business_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["info"], {"id": business_id})
        self.assertEqual(data["reviews"], {"reviews": 1})

    def test_query_yelp_business_id_empty(self):
        business_id = None
        self.assertEqual(query_yelp(business_id), None)

    def test_get_restaurant_list(self):
        create_restaurant(
            "Gary Danko", "somewhere in LIC", "11101", "WavvLdfdP6g8aZTtbBQHTw"
        )
        create_inspection_records(
            restaurant_inspection_id="27555",
            restaurant_name="Gary Danko",
            postcode="11101",
            business_address="somewhere in LIC",
            is_roadway_compliant="Compliant",
            skipped_reason="Nan",
            inspected_on=datetime(2020, 10, 24, 17, 36),
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        YelpRestaurantDetails.objects.create(business_id="WavvLdfdP6g8aZTtbBQHTw")
        data = get_restaurant_list(1, 1)
        self.assertEqual(data[0]["yelp_info"]["id"], "WavvLdfdP6g8aZTtbBQHTw")

    def test_get_latest_feedback(self):
        questionnaire_old = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        questionnaire_new = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now() + timedelta(hours=1),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        latest_feedback = get_latest_feedback("WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(latest_feedback, model_to_dict(questionnaire_new))
        self.assertNotEqual(latest_feedback, model_to_dict(questionnaire_old))

    def test_get_average_safety_rating(self):
        UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="1",
            saved_on=datetime.now(),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="2",
            saved_on=datetime.now() + timedelta(hours=1),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="3",
            saved_on=datetime.now() + timedelta(hours=2),
            temperature_required="True",
            contact_info_required="True",
            employee_mask="True",
            capacity_compliant="True",
            distance_compliant="True",
        )
        average_safety = get_average_safety_rating("WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(average_safety, "2.0")


class IntegratedInspectionRestaurantsTests(TestCase):
    """ Test Restaurant Views """

    def test_valid_get_latest_inspections(self):
        restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            postcode="10040",
            business_id="16",
        )
        InspectionRecords.objects.create(
            restaurant_inspection_id="24111",
            restaurant_name="Tacos El Paisa",
            postcode="10040",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            is_roadway_compliant="Compliant",
            skipped_reason="No Seating",
            inspected_on=datetime(2020, 10, 21, 12, 30, 30),
        )
        target_inspection = InspectionRecords.objects.create(
            restaurant_inspection_id="24112",
            restaurant_name="Tacos El Paisa",
            postcode="10040",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            is_roadway_compliant="Non-Compliant",
            skipped_reason="No Seating",
            inspected_on=datetime(2020, 10, 22, 12, 30, 30),
        )

        latest_inspection = get_latest_inspection_record(
            restaurant.restaurant_name,
            restaurant.business_address,
            restaurant.postcode,
        )
        record = model_to_dict(target_inspection)
        record["inspected_on"] = record["inspected_on"].strftime("%Y-%m-%d %I:%M %p")

        self.assertEqual(latest_inspection, record)

    @mock.patch("restaurant.utils.InspectionRecords.objects.filter")
    def test_get_latest_inspections_empty(self, mock_records):
        mock_records.return_value = InspectionRecords.objects.none()

    def test_invalid_get_inspection_info(self):
        restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            postcode="10040",
            business_id="16",
        )
        latest_inspection = get_latest_inspection_record(
            restaurant.restaurant_name,
            restaurant.business_address,
            restaurant.postcode,
        )
        self.assertEqual(latest_inspection, None)


class GetFilteredRestaurantsTests(TestCase):
    """ Test Filter Restaurants module"""

    def test_get_filtered_restaurants(self):
        cat = Categories.objects.create(category="wine_bar", parent_category="bars")
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        neighborhood = "Upper East Side"
        price = "$$"
        rating = 4.0
        img_url = "https://s3-media1.fl.yelpcdn.com/bphoto/C4emY32GDusdMCybR6NmpQ/o.jpg"
        latitude = 40.8522129
        longitude = -73.8290069
        page = 0
        limit = 4

        details = create_yelp_restaurant_details(
            business_id,
            neighborhood,
            price,
            rating,
            img_url,
            latitude,
            longitude,
        )

        details.category.add(cat)
        details.save()
        create_restaurant(
            business_id=business_id,
            business_address="fake addres",
            postcode="11111",
            restaurant_name="Test Italian Restaurant",
        )
        filtered_restaurants = get_filtered_restaurants(
            price=["$$"],
            neighborhood=["Upper East Side"],
            rating=[4.0],
            page=page,
            limit=limit,
        )

        self.assertEqual(details.business_id, filtered_restaurants[0].business_id)


class GetInspectionDataTests(TestCase):
    """ Test Get/Save Inspection data Script"""

    # def test_clean_inspection_data(self):
    #     result = [
    #         {
    #             "borough": "Manhattan",
    #             "restaurantname": "AJISEN RAMEN",
    #             "seatingchoice": "both",
    #             # "legalbusinessname": "AJISEN RAMEN CHELSEA INC.",
    #             "businessaddress": "136 WEST 28TH STREET",
    #             "restaurantinspectionid": "25808",
    #             "isroadwaycompliant": "Skipped Inspection",
    #             "skippedreason": "No Seating",
    #             "inspectedon": "2020-10-19T10:57:21.000",
    #             "agencycode": "DOT",
    #             "postcode": "10001",
    #             "latitude": "40.746520",
    #             "longitude": "-73.991678",
    #             "communityboard": "5",
    #             "councildistrict": "3",
    #             "censustract": "95",
    #             "bin": "1015092",
    #             "bbl": "1008030060",
    #             "nta": "Midtown-Midtown South",
    #         }
    #     ]
    #
    #     results_df = pd.DataFrame.from_records(result)
    #     restaurant = [
    #         {
    #             "restaurantname": "AJISEN RAMEN",
    #             # "legalbusinessname": "AJISEN RAMEN CHELSEA INC.",
    #             "businessaddress": "136 WEST 28TH STREET",
    #             "postcode": "10001",
    #         }
    #     ]
    #     r_df = pd.DataFrame.from_records(restaurant)
    #     restaurant_df, inspection_df = clean_inspection_data(results_df)
    #
    #     assert_frame_equal(restaurant_df, r_df)

    # def test_match_on_yelp(self):
    #     restaurant_name = "AJISEN RAMEN"
    #     restaurant_location = "136 WEST 28TH STREET"
    #     b_id = "2SMaAUcbNjW7vSwdg38P2Q"
    #     response = json.loads(match_on_yelp(restaurant_name, restaurant_location))
    #
    #     self.assertEqual(response["businesses"][0]["id"], b_id)

    # def test_save_restaurants(self):
    #     restaurant = [
    #         {
    #             "restaurantname": "AJISEN RAMEN",
    #             # "legalbusinessname": "AJISEN RAMEN CHELSEA INC.",
    #             "businessaddress": "136 WEST 28TH STREET",
    #             "postcode": "10001",
    #         }
    #     ]
    #     r_df = pd.DataFrame.from_records(restaurant)
    #
    #     save_restaurants(r_df)
    #
    #     return True

    # @mock.patch("getinspection.match_on_yelp")
    # def test_save_restaurants_catch(self, mock_match_on_yelp):
    #     restaurant = [
    #         {
    #             "restaurantname": "AJISEN RAMEN",
    #             # "legalbusinessname": "AJISEN RAMEN CHELSEA INC.",
    #             "businessaddress": "136 WEST 28TH STREET",
    #             "postcode": "10001",
    #         }
    #     ]
    #     r_df = pd.DataFrame.from_records(restaurant)
    #
    #     # business_id = "2SMaAUcbNjW7vSwdg38P2Q"
    #     mock_match_on_yelp.return_value = MockResponse(
    #         {
    #             "businesses": [
    #                 {
    #                     "id": "2SMaAUcbNjW7vSwdg38P2Q",
    #                     "alias": "ajisen-ramen-new-york-2",
    #                     "name": "Ajisen Ramen",
    #                     "coordinates": {"latitude": 40.74661, "longitude": -73.9921},
    #                     "location": {
    #                         "address1": "136 W 28th St",
    #                         "address2": None,
    #                         "address3": "",
    #                         "city": "New York",
    #                         "zip_code": "10001",
    #                         "country": "US",
    #                         "state": "NY",
    #                         "display_address":
    #                         ["136 W 28th St", "New York, NY 10001"],
    #                     },
    #                     "phone": "+16466380888",
    #                     "display_phone": "(646) 638-0888",
    #                 }
    #             ]
    #         },
    #         200,
    #     )
    #
    #     save_restaurants(r_df)
    #
    #     return True

    # def test_save_inspections(self):
    #     inspections = [
    #         {
    #             "restaurantname": "AJISEN RAMEN",
    #             "businessaddress": "136 WEST 28TH STREET",
    #             "restaurantinspectionid": "25808",
    #             "isroadwaycompliant": "Skipped Inspection",
    #             "skippedreason": "No Seating",
    #             "inspectedon": "2020-10-19T10:57:21.000",
    #             "postcode": "10001",
    #         }
    #     ]
    #
    #     in_rec_df = pd.DataFrame.from_records(inspections)
    #
    #     save_inspections(in_rec_df)
    #
    #     return True

    # @mock.patch("getinspection.clean_inspection_data")
    # @mock.patch("getinspection.save_restaurants")
    # @mock.patch("getinspection.save_inspections")
    # @mock.patch("getinspection.get_inspection_data.client.get")

    # def test_get_inspection_data(self,
    #                              mock_clean_inspection_data,
    #                              mock_save_restaurants,
    #                              mock_save_inspections):
    #     inspection1 = InspectionRecords.objects.create(
    #         restaurant_Inspection_ID="24111",
    #         restaurant_name="Tacos El Paisa",
    #         postcode="10040",
    #         business_address="1548 St. Nicholas btw West 187th street and west 188th "
    #                          "street, Manhattan, NY",
    #         is_roadway_compliant="Compliant",
    #         skipped_reason="No Seating",
    #         inspected_on=datetime(2020, 10, 21, 12, 30, 30),
    #     )
    #     inspection2 = InspectionRecords.objects.create(
    #         restaurant_Inspection_ID="24112",
    #         restaurant_name="Tacos El Paisa",
    #         postcode="10040",
    #         business_address="1548 St. Nicholas btw West 187th street and west 188th "
    #                          "street, Manhattan, NY",
    #         is_roadway_compliant="Non-Compliant",
    #         skipped_reason="No Seating",
    #         inspected_on=datetime(2020, 10, 22, 12, 30, 30),
    #     )
    #     # mock_get.return_value = [
    #     #         {
    #     #             "borough": "Manhattan",
    #     #             "restaurantname": "AJISEN RAMEN",
    #     #             "seatingchoice": "both",
    #     #             "legalbusinessname": "AJISEN RAMEN CHELSEA INC.",
    #     #             "businessaddress": "136 WEST 28TH STREET",
    #     #             "restaurantinspectionid": "25808",
    #     #             "isroadwaycompliant": "Skipped Inspection",
    #     #             "skippedreason": "No Seating",
    #     #             "inspectedon": "2020-10-19T10:57:21.000",
    #     #             "agencycode": "DOT",
    #     #             "postcode": "10001",
    #     #             "latitude": "40.746520",
    #     #             "longitude": "-73.991678",
    #     #             "communityboard": "5",
    #     #             "councildistrict": "3",
    #     #             "censustract": "95",
    #     #             "bin": "1015092",
    #     #             "bbl": "1008030060",
    #     #             "nta": "Midtown-Midtown South"
    #     #         }
    #     #     ]
    #     inspections = [
    #         {'restaurantname': 'AJISEN RAMEN',
    #          'businessaddress': '136 WEST 28TH STREET',
    #          'restaurantinspectionid': '25808',
    #          'isroadwaycompliant': 'Skipped Inspection',
    #          'skippedreason': 'No Seating',
    #          'inspectedon': '2020-10-19T10:57:21.000',
    #          'postcode': '10001'}
    #     ]
    #     in_rec_df = pd.DataFrame.from_records(inspections)
    #
    #     restaurant = [
    #         {'restaurantname': 'AJISEN RAMEN',
    #          'legalbusinessname': 'AJISEN RAMEN CHELSEA INC.',
    #          'businessaddress': '136 WEST 28TH STREET',
    #          'postcode': '10001'}
    #     ]
    #     r_df = pd.DataFrame.from_records(restaurant)
    #
    #     mock_clean_inspection_data.return_value = r_df
    #     mock_save_restaurants = True
    #     mock_save_inspections = True
    #
    #     get_inspection_data()
    #
    #     return True
