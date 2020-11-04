from django.contrib import admin
from .models import InspectionRecords, Restaurant, UserQuestionnaire, YelpRestaurantDetails, Zipcodes
from import_export import resources
# from import_export.fields import Field

admin.site.register(Restaurant)
admin.site.register(InspectionRecords)
admin.site.register(UserQuestionnaire)
admin.site.register(YelpRestaurantDetails)
admin.site.register(Zipcodes)


class RestaurantResource(resources.ModelResource):

    class Meta:
        model = Restaurant
        fields = ("id", "restaurant_name", "business_address", "postcode", "business_id")
        export_order = ("id", "restaurant_name", "business_address", "postcode", "business_id")