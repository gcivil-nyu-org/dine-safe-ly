from django.urls import path

from restaurant import views

app_name = 'restaurant'
urlpatterns = [
    path('', views.index, name='index'),
    path('<restaurant_id>/', views.get_restaurant_by_id, name='restaurant'),
    path('data/add_inspection_records/', views.add_inspection_records),
    path('inspection_records/<name>/<address>/<postcode>', views.get_inspection_info, name='yelp_info')
]