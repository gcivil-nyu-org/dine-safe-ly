from django.test import RequestFactory, TestCase
from django.forms.models import model_to_dict
from django.test import Client
from datetime import datetime, timedelta
from unittest import mock

from django.urls import reverse

from .forms import QuestionnaireForm
from django.contrib.auth import get_user_model
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
    check_restaurant_saved,
    questionnaire_report,
    questionnaire_statistics,
)

import json


def create_restaurant(
    restaurant_name, business_address, yelp_detail, postcode, business_id
):
    return Restaurant.objects.create(
        restaurant_name=restaurant_name,
        business_address=business_address,
        yelp_detail=yelp_detail,
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
            yelp_detail=None,
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

        YelpRestaurantDetails.objects.create(
            business_id="1",
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
            yelp_detail=None,
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
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("pass123")
        self.dummy_user.save()
        self.dummy_user_questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )

        return super().setUp


class UserQuestionnaireFormTests(BaseTest):
    def test_no_business_id(self):
        self.form_no_business_id = {
            "restaurant_business_id": "",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_business_id)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_user_id(self):
        self.form_no_user_id = {
            "restaurant_business_id": "",
            "user_id": "",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_user_id)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_safety_level(self):
        self.form_no_safety_level = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
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
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_temperature_required)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_contact_info_required(self):
        self.form_no_contact_info_required = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_contact_info_required)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_employee_mask(self):
        self.form_no_employee_mask = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_employee_mask)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_capacity_compliant(self):
        self.form_no_capacity_compliant = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "",
            "distance_compliant": "true",
        }
        questionnaire_form = QuestionnaireForm(self.form_no_capacity_compliant)
        self.assertFalse(questionnaire_form.is_valid())

    def test_no_distance_compliant(self):
        self.form_no_distance_compliant = {
            "restaurant_business_id": "WavvLdfdP6g8aZTtbBQHTw",
            "user_id": "1",
            "saved_on": str(datetime.now()),
            "safety_level": "5",
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
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
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
        }
        form = QuestionnaireForm(self.form_valid)
        self.assertTrue(form.is_valid())

    def test_form_submission(self):
        create_restaurant(
            "random_name",
            "random_address",
            None,
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        self.form = {
            "restaurant_business_id": "U8C69ISrhGTTubjqoVgZYg",
            "user_id": "1",
            "safety_level": "5",
            "saved_on": datetime.now(),
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
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


class RestaurantViewFormTests(BaseTest):
    def test_restaurant_profile_view_questionnaire(self):
        create_restaurant(
            "random_name",
            "random_address",
            None,
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        self.questionnaire_form = {
            "restaurant_business_id": "U8C69ISrhGTTubjqoVgZYg",
            "user_id": "1",
            "safety_level": "5",
            "saved_on": datetime.now(),
            "temperature_required": "true",
            "contact_info_required": "true",
            "employee_mask": "true",
            "capacity_compliant": "true",
            "distance_compliant": "true",
            "questionnaire_form": "",
        }
        form = QuestionnaireForm(self.questionnaire_form)
        response = self.c.post("/restaurant/profile/1/", self.questionnaire_form)
        self.assertTrue(form.is_valid())
        self.assertEqual(response.status_code, 302)


class RestaurantViewTests(TestCase):
    """ Test Restaurant Views """

    def setUp(self):
        self.factory = RequestFactory()
        business_id = "WavvLdfdP6g8aZTtbBQHTw"
        neighborhood = "Upper East Side"
        price = "$$"
        rating = 4.0
        img_url = "https://s3-media1.fl.yelpcdn.com/bphoto/C4emY32GDusdMCybR6NmpQ/o.jpg"
        latitude = 40.8522129
        longitude = -73.8290069

        details = create_yelp_restaurant_details(
            business_id,
            neighborhood,
            price,
            rating,
            img_url,
            latitude,
            longitude,
        )
        self.restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            yelp_detail=details,
            postcode="10040",
            business_id="16",
        )

    def test_get_valid_restaurant_profile(self):
        request = self.factory.get("restaurant:profile")
        request.restaurant = self.restaurant
        request.user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
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
        request.user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        response = get_landing_page(request, 6)
        self.assertEqual(response.status_code, 200)

    def test_restaurant_profile_view_save_favorite(self):
        create_restaurant(
            "random_name",
            "random_address",
            None,
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("pass123")
        self.dummy_user.save()
        self.c = Client()
        self.c.login(username="myuser", password="pass123")

        url = reverse(
            "restaurant:save_favorite_restaurant", args=["U8C69ISrhGTTubjqoVgZYg"]
        )
        response = self.c.post(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.dummy_user.favorite_restaurants.all().count() == 1)

    def test_restaurant_profile_view_delete_favorite(self):
        create_restaurant(
            "random_name",
            "random_address",
            None,
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("pass123")
        self.dummy_user.save()
        self.c = Client()
        self.c.login(username="myuser", password="pass123")
        url = reverse(
            "restaurant:delete_favorite_restaurant", args=["U8C69ISrhGTTubjqoVgZYg"]
        )
        response = self.c.post(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.dummy_user.favorite_restaurants.all().count() == 0)


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
                    "img_url": "test_url.com",
                    "image_url": "test_url.com",
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
        self.assertEqual(data["info"]["id"], business_id)
        self.assertEqual(data["reviews"], {"reviews": 1})

    def test_query_yelp_business_id_empty(self):
        business_id = None
        self.assertEqual(query_yelp(business_id), None)

    def test_get_restaurant_list(self):
        create_restaurant(
            "Gary Danko", "somewhere in LIC", None, "11101", "WavvLdfdP6g8aZTtbBQHTw"
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
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        questionnaire_new = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now() + timedelta(hours=1),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
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
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="2",
            saved_on=datetime.now() + timedelta(hours=1),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="3",
            saved_on=datetime.now() + timedelta(hours=2),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        average_safety = get_average_safety_rating("WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(average_safety, "2.0")

    def test_check_restaurant_saved(self):
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("Dinesafely123")
        self.dummy_user.save()
        self.temp_rest = create_restaurant(
            "random_name",
            "random_address",
            None,
            "random_postcode",
            "U8C69ISrhGTTubjqoVgZYg",
        )
        self.dummy_user.favorite_restaurants.add(
            Restaurant.objects.get(business_id="U8C69ISrhGTTubjqoVgZYg")
        )
        self.assertTrue(check_restaurant_saved(self.dummy_user, 1))

    def test_questionnaire_report(self):
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("Dinesafely123")
        self.dummy_user.save()
        self.temp_rest = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            yelp_detail=None,
            postcode="10040",
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        self.temp_inspection = InspectionRecords.objects.create(
            restaurant_inspection_id="24111",
            restaurant_name="Tacos El Paisa",
            postcode="10040",
            business_address="1548 St. Nicholas btw West 187th street "
            "and west 188th "
            "street, Manhattan, NY",
            is_roadway_compliant="Compliant",
            skipped_reason="No Seating",
            inspected_on=datetime(2020, 10, 21, 12, 30, 30),
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        self.temp_user_questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        latest_inspection_status, valuable_questionnaire_list = questionnaire_report(
            "WavvLdfdP6g8aZTtbBQHTw"
        )
        self.assertEqual(latest_inspection_status, "Compliant")
        self.assertEqual(valuable_questionnaire_list[0], self.temp_user_questionnaire)

    def test_questionnaire_statistics(self):
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("Dinesafely123")
        self.dummy_user.save()
        self.temp_rest = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            yelp_detail=None,
            postcode="10040",
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        self.temp_inspection = InspectionRecords.objects.create(
            restaurant_inspection_id="24111",
            restaurant_name="Tacos El Paisa",
            postcode="10040",
            business_address="1548 St. Nicholas btw West 187th street "
            "and west 188th "
            "street, Manhattan, NY",
            is_roadway_compliant="Compliant",
            skipped_reason="No Seating",
            inspected_on=datetime(2020, 10, 21, 12, 30, 30),
            business_id="WavvLdfdP6g8aZTtbBQHTw",
        )
        self.temp_user_questionnaire_1 = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="5",
            saved_on=datetime.now(),
            temperature_required="true",
            contact_info_required="true",
            employee_mask="true",
            capacity_compliant="true",
            distance_compliant="true",
        )
        self.temp_user_questionnaire_2 = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="1",
            saved_on=datetime.now(),
            temperature_required="false",
            contact_info_required="false",
            employee_mask="false",
            capacity_compliant="false",
            distance_compliant="false",
        )
        self.temp_user_questionnaire_3 = UserQuestionnaire.objects.create(
            restaurant_business_id="WavvLdfdP6g8aZTtbBQHTw",
            user_id="1",
            safety_level="3",
            saved_on=datetime.now(),
            temperature_required="false",
            contact_info_required="false",
            employee_mask="false",
            capacity_compliant="false",
            distance_compliant="false",
        )
        statistics_dict = questionnaire_statistics("WavvLdfdP6g8aZTtbBQHTw")
        self.assertEqual(statistics_dict["valuable_avg_safety_rating"], "3.0")
        self.assertEqual(statistics_dict["temp_check_true"], 1)
        self.assertEqual(statistics_dict["contact_info_required_true"], 1)
        self.assertEqual(statistics_dict["employee_mask_true"], 1)
        self.assertEqual(statistics_dict["capacity_compliant_true"], 1)
        self.assertEqual(statistics_dict["distance_compliant_true"], 1)


class IntegratedInspectionRestaurantsTests(TestCase):
    """ Test Restaurant Views """

    def test_valid_get_latest_inspections(self):
        restaurant = create_restaurant(
            restaurant_name="Tacos El Paisa",
            business_address="1548 St. Nicholas btw West 187th street and west 188th "
            "street, Manhattan, NY",
            yelp_detail=None,
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
            yelp_detail=None,
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
            yelp_detail=None,
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
