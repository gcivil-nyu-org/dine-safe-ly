from django.urls import path

from restaurant import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<restaurant_name>/', views.get_restaurant_by_name, name='restaurant')
]