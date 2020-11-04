from django.contrib import admin
from .models import (
    InspectionRecords,
    Restaurant,
    UserQuestionnaire,
    YelpRestaurantDetails,
    Zipcodes,
)


admin.site.register(Restaurant)
admin.site.register(InspectionRecords)
admin.site.register(UserQuestionnaire)
admin.site.register(YelpRestaurantDetails)
admin.site.register(Zipcodes)
