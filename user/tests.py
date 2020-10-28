from django.test import TestCase
from django.contrib.auth.models import User
from .forms import UserCreationForm
from django.test import Client
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
            "username":"",
            "email":"abcd@gmail.com",
            "password1" : "pass123",
            "password2" : "pass123",
        }
        form = UserCreationForm(self.user_no_username)
        self.assertFalse(form.is_valid())
    
    def test_form_no_email(self):
        self.user_no_email = {
            "username":"myuser",
            "email":"",
            "password1" : "pass123",
            "password2" : "pass123",
        }
        form = UserCreationForm(self.user_no_email)
        self.assertFalse(form.is_valid())
    
    def test_form_password_dont_match(self):
        self.user_password_dont_match = {
            "username":"myuser",
            "email":"abcd@gmail.com",
            "password1" : "pass123",
            "password2" : "pa123",
        }
        form = UserCreationForm(self.user_password_dont_match)
        self.assertFalse(form.is_valid())
    
    def test_form_valid(self):
        self.user_valid = {
            "username":"myuser1",
            "email":"abcde@gmail.com",
            "password1" : "pass123",
            "password2" : "pass123",
        }
        form = UserCreationForm(self.user_valid)
        self.assertTrue(form.is_valid())
    
    def test_form_username_exists(self):
        self.user_valid = {
            "username":"myuser",
            "email":"abcde@gmail.com",
            "password1" : "pass123",
            "password2" : "pass123",
        }
        form = UserCreationForm(self.user_valid)
        form.has_error("username","Username already exists")

    def test_form_username_exists(self):
        self.user_valid = {
            "username":"myuser1",
            "email":"abcd@gmail.com",
            "password1" : "pass123",
            "password2" : "pass123",
        }
        form = UserCreationForm(self.user_valid)
        form.has_error("email","Email already exists")

class TestUserRegisterView(BaseTest):

    def test_view_register_page(self):

        response = self.c.post('/user/register', {'username': 'myuser3', 'email':'abcde@gmail.com','password1': 'pass123', 'password2':"pass123"})
        self.assertEqual(response.status_code, 302)
    
    def test__register_page_invalid_request(self):

        response = self.c.get('/user/register', {'username': 'myuser3', 'email':'abcde@gmail.com','password1': 'pass123', 'password2':"pass123"})
        self.assertEqual(response.status_code, 200)


class TestUserLoginView(BaseTest):
    def test_view_login_page(self):
        self.credentials = {
            "username":"myuser17",
            "email":"abcdefg@gmail.com",
            "password":"pass123",
        }
        User.objects.create_user(**self.credentials)
        response = self.c.post('/user/login', self.credentials)

        self.assertEqual(response.status_code, 302)
    
    def test__login_page_invalid_request(self):

        response = self.c.get('/user/login', {'username': 'myuser', 'password':"pass123"})
        self.assertEqual(response.status_code, 200)