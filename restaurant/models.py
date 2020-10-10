from django.db import models


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=200, primary_key=True)
    business_id = models.CharField(max_length=200)

    def __str__(self):
        return self.restaurant_name


class InspectionRecords(models.Model):
    restaurant_Inspection_ID = models.CharField(max_length=200, primary_key=True)
    borough = models.CharField(max_length=200)
    restaurant_name = models.CharField(max_length=200)
    seating_choice = models.CharField(max_length=200)
    legal_bussiness_name = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    is_sideway_compliant = models.CharField(max_length=200)
    is_roadway_compliant = models.CharField(max_length=200)
    skipped_reason = models.CharField(max_length=200)
    inspected_on = models.DateTimeField()
    agency_code = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)