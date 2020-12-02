from django.urls import path

from restaurant import views

app_name = "restaurant"
urlpatterns = [
    path("profile/<restaurant_id>/", views.get_restaurant_profile, name="profile"),
    path(
        "inspection_records/<restaurant_id>",
        views.get_inspection_info,
        name="inspection_history",
    ),
    path("", views.get_landing_page, name="browse"),
    path("<page>", views.get_landing_page, name="browse"),
    path(
        "search_filter/restaurants_list/<page>",
        views.get_restaurants_list,
        name="restaurants_list",
    ),
    path(
        "save/favorite/restaurant/<business_id>",
        views.save_favorite_restaurant,
        name="save_favorite_restaurant",
    ),
    path(
        "delete/favorite/restaurant/<business_id>",
        views.delete_favorite_restaurant,
        name="delete_favorite_restaurant",
    ),
    path("chatbot/keywordtest", views.chatbot_keyword, name="chatbottest"),
]
