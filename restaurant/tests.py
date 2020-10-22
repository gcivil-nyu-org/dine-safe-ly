import enum
from django.test import TestCase

from .models import InspectionRecords, Restaurant


class Compliance(enum.Enum):
    no = "Non-Compliant"
    yes = "Compliant"
    skipped = "Skipped Inspection"


def create_restaurant(name, address, postcode, business_id):
    return Restaurant.objects.create(restaurant_name=name, business_address=address, postcode=postcode,
                                     business_id=business_id)


def create_inspection_records(restaurant_inspection_id, name, postcode, business_address,
                              compliance_status, skipped_reason, inspected_on):

    if not isinstance(compliance_status, Compliance):
        raise TypeError('compliance_status must be an instance of Compliance enum')

    return InspectionRecords.objects.create(restaurant_inspection_id=restaurant_inspection_id, restaurant_name=name,
                                            postcode=postcode, business_address=business_address,
                                            is_roadway_compliant=compliance_status,
                                            skipped_reason=skipped_reason, inspected_on=inspected_on)


class InspectionRecordsViewTests(TestCase):
    """ Test InspectionRecords Views """


class RestaurantViewTests(TestCase):
    """ Test Restaurant Views """
