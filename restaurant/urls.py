from django.urls import path

from restaurant import views

app_name = "restaurant"
urlpatterns = [
    path("", views.index, name="index"),
    path("profile/<restaurant_id>/", views.get_restaurant_profile, name="profile"),
    path(
        "inspection_records/<restaurant_id>",
        views.get_inspection_info,
        name="inspection_history",
    ),
    path("browse/", views.get_landing_page, name="browse"),
    path("browse/<page>", views.get_landing_page, name="browse"),
]
