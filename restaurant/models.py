from django.db import models


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    business_id = models.CharField(max_length=200, default=None, blank=True, null=True)

    class Meta:
        unique_together = (("restaurant_name", "business_address", "postcode"),)

    def __str__(self):
        return "{} {} {} {} {}".format(
            self.id,
            self.restaurant_name,
            self.business_address,
            self.postcode,
            self.business_id,
        )


class InspectionRecords(models.Model):
    restaurant_inspection_id = models.CharField(max_length=200, primary_key=True)
    restaurant_name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    business_address = models.CharField(max_length=200)
    is_roadway_compliant = models.CharField(max_length=200)
    skipped_reason = models.CharField(max_length=200)
    inspected_on = models.DateTimeField()

    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            self.restaurant_inspection_id,
            self.restaurant_name,
            self.is_roadway_compliant,
            self.skipped_reason,
            self.inspected_on,
            self.postcode,
            self.business_address,
        )


class UserQuestionnaire(models.Model):
    # the restaurant the feedback is for
    restaurant_business_id = models.CharField(max_length=200, blank=True, null=True)
    # indicate your level or satisfaction for this restaurant
    satisfaction_level = models.CharField(max_length=200)
    # indicate your level of safety for this restaurant
    safety_level = models.CharField(max_length=200)
    mask_required = models.CharField(max_length=200)
    temperature_required = models.CharField(max_length=200)
    would_recommend = models.CharField(max_length=200)

    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            self.restaurant_business_id,
            self.satisfaction_level,
            self.safety_level,
            self.mask_required,
            self.temperature_required,
            self.would_recommend,
        )
