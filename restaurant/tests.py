import enum
from django.test import TestCase
from django.urls import reverse

from .models import InspectionRecords, Restaurant


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


def setup():
    create_inspection_records(restaurant_Inspection_ID='11157', restaurant_name='Tacos El Paisa', postcode='10040',
                              business_address='1548 St. Nicholas btw West 187th street and west 188th street, '
                                               'Manhattan, NY', is_roadway_compliant=Compliance.skipped,
                              skipped_reason='No Seating', inspected_on='2020-07-16 18:09:42')

    test_restaurant = create_restaurant(restaurant_name='Tacos El Paisa',
                                        business_address='1548 St. Nicholas btw West 187th street and west 188th '
                                                         'street, Manhattan, NY',
                                        postcode='10040', business_id='16')
    return test_restaurant


class InspectionRecordsViewTests(TestCase):
    """ Tests """

    def test_get_valid_restaurant_inspections(self):
        restaurant = setup()
        response = self.client.get(reverse('restaurant:inspection_history', args=(restaurant.id,)))
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_restaurant_inspections(self):
        restaurant = setup()
        restaurant.id = -1
        response = self.client.get(reverse('restaurant:inspection_history', args=(restaurant.id,)))
        self.assertEqual(response.status_code, 404)


class RestaurantViewTests(TestCase):
    """ Test Restaurant Views """
