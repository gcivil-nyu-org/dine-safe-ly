from django.db import models


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    business_id = models.CharField(max_length=200, default=None)
    legal_business_name = models.CharField(max_length=200,default = None)

    class Meta:
        unique_together = (('restaurant_name', 'legal_business_name', 'postcode'),)

    def __str__(self):
        return self.restaurant_name


class InspectionRecords(models.Model):
    restaurant_Inspection_ID = models.CharField(max_length=200, primary_key=True)
    restaurant_name = models.CharField(max_length=200)
    is_sideway_compliant = models.CharField(max_length=200)
    is_roadway_compliant = models.CharField(max_length=200)
    skipped_reason = models.CharField(max_length=200)
    inspected_on = models.DateTimeField()
    agency_code = models.CharField(max_length=200)