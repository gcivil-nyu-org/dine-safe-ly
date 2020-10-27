from django.urls import path

from user import views

app_name = "user"
urlpatterns = [
    path("login", views.user_login, name="login"),
    path("logout", views.post_logout, name="logout"),
    path("register", views.register, name="register"),
]
