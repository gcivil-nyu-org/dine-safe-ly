from django.db import models


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    business_id = models.CharField(max_length=200, default=None, blank=True, null=True)
    legal_business_name = models.CharField(max_length=200, default=None)

    class Meta:
        unique_together = (('restaurant_name', 'business_address', 'postcode'),)

    def __str__(self):
        return '{} {} {} {} {} {}'.format(self.id, self.restaurant_name, self.business_address, self.postcode, self.legal_business_name, self.business_id) 



class InspectionRecords(models.Model):
    restaurant_Inspection_ID = models.CharField(max_length=200, primary_key=True)
    restaurant_name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    is_roadway_compliant = models.CharField(max_length=200)
    skipped_reason = models.CharField(max_length=200)
    inspected_on = models.DateTimeField()
    

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(self.restaurant_Inspection_ID, self.restaurant_name, self.is_roadway_compliant,self.skipped_reason, self.inspected_on, self.postcode, self.business_address)
