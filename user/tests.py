from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from restaurant.models import Categories
from .forms import (
    UserCreationForm,
    ResetPasswordForm,
    GetEmailForm,
    UpdatePasswordForm,
    UserPreferenceForm,
)
from .utils import send_reset_password_email
from django.test import Client
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes


# Create your tests here.


class BaseTest(TestCase):
    def setUp(self):
        self.user_register_url = "user:register"
        self.c = Client()
        self.dummy_user = get_user_model().objects.create(
            username="myuser",
            email="abcd@gmail.com",
        )
        self.dummy_user.set_password("pass123")
        self.dummy_user.save()
        return super().setUp


class TestUserModel(BaseTest):
    def test_create_user(self):
        temp_user = get_user_model().objects.create_user("xiong")
        self.assertEqual(temp_user.username, "xiong")


class TestUserCreationForm(BaseTest):
    # def test_form_no_username(self):
    #     self.user_no_username = {
    #         "username": "",
    #         "email": "abcd@gmail.com",
    #         "password1": "pass123",
    #         "password2": "pass123",
    #     }
    #     form = UserCreationForm(self.user_no_username)
    #     self.assertFalse(form.is_valid())

    # def test_form_no_email(self):
    #     self.user_no_email = {
    #         "username": "myuser",
    #         "email": "",
    #         "password1": "pass123",
    #         "password2": "pass123",
    #     }
    #     form = UserCreationForm(self.user_no_email)
    #     self.assertFalse(form.is_valid())

    # def test_form_password_dont_match(self):
    #     self.user_password_dont_match = {
    #         "username": "myuser",
    #         "email": "abcd@gmail.com",
    #         "password1": "pass123",
    #         "password2": "pa123",
    #     }
    #     form = UserCreationForm(self.user_password_dont_match)
    #     self.assertFalse(form.is_valid())

    def test_form_valid(self):
        self.user_valid = {
            "username": "myuser1",
            "email": "abcde@gmail.com",
            "password1": "dinesafelypass123",
            "password2": "dinesafelypass123",
        }
        form = UserCreationForm(self.user_valid)
        self.assertTrue(form.is_valid())

    # def test_form_username_exists(self):
    #     self.user_valid = {
    #         "username": "myuser",
    #         "email": "abcde@gmail.com",
    #         "password1": "pass123",
    #         "password2": "pass123",
    #     }
    #     form = UserCreationForm(self.user_valid)
    #     form.has_error("username", "Username already exists")

    # def test_form_email_exists(self):
    #     self.user_valid = {
    #         "username": "myuser1",
    #         "email": "abcd@gmail.com",
    #         "password1": "pass123",
    #         "password2": "pass123",
    #     }
    #     form = UserCreationForm(self.user_valid)
    #     form.has_error("email", "Email already exists")


class TestResetPasswordForm(BaseTest):
    def test_form_password_dont_match(self):
        self.user_password_dont_match = {
            "password1": "dinesafelyhardPass123",
            "password2": "padinesafelyhardPass1234",
        }
        form = ResetPasswordForm(self.user_password_dont_match)
        self.assertFalse(form.is_valid())

    def test_save_password(self):
        # self.test_save_password = {
        #     "password1": "pass123",
        #     "password2": "pass123",
        # }
        # form = ResetPasswordForm(self.test_save_password)
        user = self.dummy_user

        response = self.c.post(
            "/user/reset_password/"
            + urlsafe_base64_encode(force_bytes(user.pk))
            + "/"
            + PasswordResetTokenGenerator().make_token(user),
            {"password1": "dinesafely1234", "password2": "dinesafely1234"},
        )
        # redirect to login page after reset
        self.assertEqual(response.status_code, 302)


class TestGetEmailForm(BaseTest):
    def test_email_valid(self):
        email_form = {"email": self.dummy_user.email}
        form = GetEmailForm(email_form)
        self.assertEqual(form.is_valid(), True)

    def test_email_invalid(self):
        email_form = {"email": "fake@email.com"}
        form = GetEmailForm(email_form)
        self.assertFalse(form.is_valid())


class TestUpdatePasswordForm(BaseTest):
    def test_update_password_form_invalid(self):
        form_data = {
            "password_current": "pass123",
            "password_new": "123456",
            "password_confirm": "1234567",
        }
        form = UpdatePasswordForm(user=self.dummy_user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_verify_user(self):
        user = self.dummy_user

        response = self.c.post(
            "/user/verification/"
            + urlsafe_base64_encode(force_bytes(user.pk))
            + "/"
            + PasswordResetTokenGenerator().make_token(user)
        )
        # redirect to login page after reset
        self.assertEqual(response.status_code, 302)


class TestUserPreferenceForm(BaseTest):
    def test_user_pref_form_valid(self):
        form_data = {
            "pref_list": [
                "sushi",
                "french",
            ]
        }
        user_pref_form = UserPreferenceForm(data=form_data)
        self.assertTrue(user_pref_form.is_valid())


class TestUtils(BaseTest):
    class MockRequest:
        host_name = "localhost"

        def get_host(self):
            return self.host_name

    def test_send_reset_password_email(self):
        self.assertEqual(
            send_reset_password_email(self.MockRequest(), self.dummy_user.email), 1
        )


class TestUserRegisterView(BaseTest):
    def test_view_register_page(self):
        response = self.c.post(
            "/user/register",
            {
                "username": "user_test_for_register",
                "email": "abcde@gmail.com",
                "password1": "hardPass123",
                "password2": "hardPass123",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test__register_page_invalid_request(self):
        response = self.c.get(
            "/user/register",
            {
                "username": "myuser3",
                "email": "abcde@gmail.com",
                "password1": "pass123",
                "password2": "pass123",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_logout_request(self):
        response = self.c.post("/user/logout")
        self.assertEqual(response.status_code, 302)

    def test_already_logged_in_register_page(self):
        self.c.force_login(self.dummy_user)
        response = self.c.get("/user/register")
        self.assertEqual(response.status_code, 302)


class TestUserLoginView(BaseTest):
    def test_already_logged_in_login_page(self):
        self.c.force_login(self.dummy_user)
        response = self.c.get("/user/login")
        self.assertEqual(response.status_code, 302)

    def test_view_login_page(self):
        self.credentials = {
            "username": "myuser17",
            "email": "abcdefg@gmail.com",
            "password": "pass123",
        }
        get_user_model().objects.create_user(**self.credentials)
        response = self.c.post("/user/login", self.credentials)

        self.assertEqual(response.status_code, 302)

    def test__login_page_invalid_request(self):
        response = self.c.get(
            "/user/login", {"username": "myuser", "password": "pass123"}
        )
        self.assertEqual(response.status_code, 200)


class TestUpdatePasswordView(BaseTest):
    def test_no_user_logged_in(self):
        response = self.c.get("/user/update_password")
        self.assertEqual(response.status_code, 302)

    def test_update_password_save(self):
        self.c.force_login(self.dummy_user)
        response = self.c.post(
            "/user/update_password",
            {
                "password_current": "pass123",
                "password_new": "ReallyHardPassword123!",
                "password_confirm": "ReallyHardPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_update_password_invalid_form(self):
        self.c.force_login(self.dummy_user)
        response = self.c.post(
            "/user/update_password",
            {
                "password_current": "pass123",
                "password_new": "ReallyHardPassword123!",
                "password_confirm": "FakePassword!",
                "update_pass_form": "",
            },
        )
        self.assertEqual(response.status_code, 400)


class TestAccountDetailsView(BaseTest):
    def test_no_user_logged_in(self):
        response = self.c.get("/user/account_details")
        self.assertEqual(response.status_code, 302)

    def test_user_login(self):
        self.c.force_login(self.dummy_user)
        response = self.c.get("/user/account_details")
        self.assertEqual(response.status_code, 200)


class TestForgetPasswordView(BaseTest):
    def test_forget_password_valid_email(self):
        response = self.c.post(
            "/user/forget_password",
            {
                "email": "abcd@gmail.com",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_forget_password_invalid_email(self):
        response = self.c.post(
            "/user/forget_password",
            {
                "email": "fake_email",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_forget_password_no_post(self):
        response = self.c.get(
            "/user/forget_password",
            {
                "email": "fake_email",
            },
        )
        self.assertEqual(response.status_code, 200)


class TestAddPrefView(BaseTest):
    def test_add_pref_valid(self):
        self.c.login(username="myuser", password="pass123")
        Categories.objects.create(category="sushi", parent_category="sushi")
        Categories.objects.create(category="french", parent_category="french")
        url = reverse("user:add_preference")
        form_data = {
            "pref_list": [
                "sushi",
                "french",
            ]
        }
        user_pref_form = UserPreferenceForm(form_data)
        self.assertTrue(user_pref_form.is_valid())
        response = self.c.post(path=url, data=form_data)
        self.assertEqual(response.status_code, 200)


class TestDeletePrefView(BaseTest):
    def test_del_pref_valid(self):
        self.c.login(username="myuser", password="pass123")
        url = reverse("user:delete_preference", args=["sushi"])
        Categories.objects.create(category="sushi", parent_category="sushi")
        Categories.objects.create(category="french", parent_category="french")
        response = self.c.post(path=url)
        self.assertEqual(response.status_code, 200)
