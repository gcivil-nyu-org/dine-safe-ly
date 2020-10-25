from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.


class TestUserModel(TestCase):
    def test_create_user(self):
        temp_user = User.objects.create_user("xiong")
        self.assertEqual(temp_user.username, "xiong")
