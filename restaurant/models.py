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
    restaurant_business_id = models.CharField(max_length=200, null=False)
    safety_level = models.CharField(max_length=1)

    temperature_required = models.CharField(max_length=5, null=False, default="False")
    contact_info_required = models.CharField(max_length=5, null=False, default="False")
    employee_mask = models.CharField(max_length=5, null=False, default="False")
    capacity_compliant = models.CharField(max_length=5, null=False, default="False")
    distance_compliant = models.CharField(max_length=5, null=False, default="False")

    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            self.restaurant_business_id,
            self.safety_level,
            self.temperature_required,
            self.contact_info_required,
            self.employee_mask,
            self.capacity_compliant,
            self.distance_compliant,
        )


class YelpRestaurantDetails(models.Model):
    business_id = models.CharField(max_length=200, primary_key=True)
    neighborhood = models.CharField(max_length=200, default=None, null=True)
    category = models.CharField(max_length=200, default=None, null=True)
    price = models.CharField(max_length=200, default=None, null=True)
    rating = models.CharField(max_length=200, default=None, null=True)
    img_url = models.CharField(max_length=200, default=None, null=True)

    def __str__(self):
        return "{} {} {} {} {} {}".format(
            self.business_id,
            self.neighborhood,
            self.category,
            self.price,
            self.rating,
            self.img_url,
        )


class Zipcodes(models.Model):
    zipcode = models.CharField(max_length=200, primary_key=True)
    borough = models.CharField(max_length=200, default=None, null=True)
    neighborhood = models.CharField(max_length=200, default=None, null=True)

    def __str__(self):
        return "{} {} {}".format(self.zipcode, self.borough, self.neighborhood)
