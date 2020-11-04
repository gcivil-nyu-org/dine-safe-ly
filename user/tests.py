from django.test import TestCase
from django.contrib.auth.models import User
from .forms import UserCreationForm, ResetPasswordForm, GetEmailForm, UpdatePasswordForm
from .utils import send_reset_password_email
from django.test import Client

# from unittest import mock
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from unittest import mock

# Create your tests here.


class BaseTest(TestCase):
    def setUp(self):
        self.user_register_url = "user:register"
        self.c = Client()
        self.dummy_user = User.objects.create(
            username="myuser",
            email="abcd@gmail.com",
            password="pass123",
        )

        return super().setUp


class TestUserModel(BaseTest):
    def test_create_user(self):
        temp_user = User.objects.create_user("xiong")
        self.assertEqual(temp_user.username, "xiong")


class TestUserCreationForm(BaseTest):
    def test_form_no_username(self):
        self.user_no_username = {
            "username": "",
            "email": "abcd@gmail.com",
            "password1": "pass123",
            "password2": "pass123",
        }
        form = UserCreationForm(self.user_no_username)
        self.assertFalse(form.is_valid())

    def test_form_no_email(self):
        self.user_no_email = {
            "username": "myuser",
            "email": "",
            "password1": "pass123",
            "password2": "pass123",
        }
        form = UserCreationForm(self.user_no_email)
        self.assertFalse(form.is_valid())

    def test_form_password_dont_match(self):
        self.user_password_dont_match = {
            "username": "myuser",
            "email": "abcd@gmail.com",
            "password1": "pass123",
            "password2": "pa123",
        }
        form = UserCreationForm(self.user_password_dont_match)
        self.assertFalse(form.is_valid())

    def test_form_valid(self):
        self.user_valid = {
            "username": "myuser1",
            "email": "abcde@gmail.com",
            "password1": "pass123",
            "password2": "pass123",
        }
        form = UserCreationForm(self.user_valid)
        self.assertTrue(form.is_valid())

    def test_form_username_exists(self):
        self.user_valid = {
            "username": "myuser",
            "email": "abcde@gmail.com",
            "password1": "pass123",
            "password2": "pass123",
        }
        form = UserCreationForm(self.user_valid)
        form.has_error("username", "Username already exists")

    def test_form_email_exists(self):
        self.user_valid = {
            "username": "myuser1",
            "email": "abcd@gmail.com",
            "password1": "pass123",
            "password2": "pass123",
        }
        form = UserCreationForm(self.user_valid)
        form.has_error("email", "Email already exists")


class TestResetPasswordForm(BaseTest):
    def test_form_password_dont_match(self):
        self.user_password_dont_match = {
            "password1": "pass123",
            "password2": "pa123",
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
            {"password1": "pass123", "password2": "pass123"},
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


class TestUserRegisterView(BaseTest):
    def test_view_register_page(self):

        response = self.c.post(
            "/user/register",
            {
                "username": "myuser3",
                "email": "abcde@gmail.com",
                "password1": "pass123",
                "password2": "pass123",
            },
        )
        self.assertEqual(response.status_code, 302)

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


class TestUserLoginView(BaseTest):
    def test_view_login_page(self):
        self.credentials = {
            "username": "myuser17",
            "email": "abcdefg@gmail.com",
            "password": "pass123",
        }
        User.objects.create_user(**self.credentials)
        response = self.c.post("/user/login", self.credentials)

        self.assertEqual(response.status_code, 302)

    def test__login_page_invalid_request(self):

        response = self.c.get(
            "/user/login", {"username": "myuser", "password": "pass123"}
        )
        self.assertEqual(response.status_code, 200)


class TestUtils(BaseTest):
    class MockRequest:
        host_name = "localhost"

        def get_host(self):
            return self.host_name

    def test_send_reset_password_email(self):
        self.assertEqual(
            send_reset_password_email(self.MockRequest(), self.dummy_user.email), 1
        )


class TestUpdatePasswordView(BaseTest):
    @mock.patch("user.forms.User.check_password")
    def test_update_password_save(self, mock_password):
        self.c.force_login(self.dummy_user)
        mock_password.return_value = True
        response = self.c.post(
            "/user/update_password",
            {
                "password_current": "pass123",
                "password_new": "pass123",
                "password_confirm": "pass123",
            },
        )
        self.assertEqual(response.status_code, 302)
