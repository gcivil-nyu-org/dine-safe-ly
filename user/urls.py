from django.urls import path
from user import views

app_name = "user"
urlpatterns = [
    path("login", views.user_login, name="login"),
    path("logout", views.post_logout, name="logout"),
    path("register", views.register, name="register"),
    path(
        "reset_password/<base64_id>/<token>",
        views.reset_password_link,
        name="reset_password",
    ),
    path("forget_password", views.forget_password, name="forget_password"),
    path("account_details", views.account_details, name="account_details"),
]
