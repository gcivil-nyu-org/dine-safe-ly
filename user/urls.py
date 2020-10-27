from django.urls import path

from user import views

app_name = "user"
urlpatterns = [
    path("login", views.get_login_page, name="login"),
    path("logout", views.post_logout, name="logout"),
    path("register", views.register_request, name="register")
]
