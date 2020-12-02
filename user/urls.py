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
    path(
        "verification/<base64_id>/<token>",
        views.verify_user_link,
        name="verify_user_link",
    ),
    path("forget_password", views.forget_password, name="forget_password"),
    path("verification", views.forget_password, name="verification"),
    path("account_details", views.account_details, name="account_details"),
    path("update_password", views.update_password, name="update_password"),
    path(
        "add/preference/user",
        views.add_preference,
        name="add_preference",
    ),
    path(
        "delete/preference/user/<category>",
        views.delete_preference,
        name="delete_preference",
    ),
]
