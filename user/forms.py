from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
import logging

from restaurant.models import Categories

logger = logging.getLogger(__name__)


class UserCreationForm(forms.Form):
    username = forms.CharField(label="Enter Username", min_length=4, max_length=150)
    email = forms.EmailField(label="Enter email")
    password1 = forms.CharField(label="Enter password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        r = get_user_model().objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not email:
            raise ValidationError("Email is required")
        r = get_user_model().objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def clean_password1(self):
        user = User(
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password1"),
        )
        password_validators = [
            MinimumLengthValidator(),
            UserAttributeSimilarityValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator(),
        ]

        try:
            validate_password(
                password=self.cleaned_data["password1"],
                user=user,
                password_validators=password_validators,
            )
            return self.cleaned_data["password1"]
        except ValidationError as e:
            logger.error("validation failed")
            raise ValidationError(e)

    def save(self, commit=True):
        user = get_user_model().objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
        )
        user.set_password(self.cleaned_data["password1"])

        return user


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        user = User(
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password2"),
        )
        password_validators = [
            MinimumLengthValidator(),
            UserAttributeSimilarityValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator(),
        ]

        try:
            validate_password(
                password=self.cleaned_data["password2"],
                user=user,
                password_validators=password_validators,
            )
        except ValidationError as e:
            logger.error("validation failed")
            raise ValidationError(e)
        return self.cleaned_data["password2"]

    def save(self, uid, commit=True):
        user = get_user_model().objects.get(pk=uid)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class UpdatePasswordForm(forms.Form):
    password_current = forms.CharField(
        label="password_current", widget=forms.PasswordInput
    )
    password_new = forms.CharField(label="password_new", widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        label="password_confirm", widget=forms.PasswordInput
    )

    def __init__(self, user, data=None):
        self.user = user
        super(UpdatePasswordForm, self).__init__(data=data)

    def clean_password_current(self):
        if not self.user.check_password(
            self.cleaned_data.get("password_current", None)
        ):
            raise ValidationError("Current password is incorrect")

    def clean_password_confirm(self):
        password1 = self.cleaned_data.get("password_new")
        password2 = self.cleaned_data.get("password_confirm")

        if password1 and password2 and password1 != password2:
            raise ValidationError("New passwords don't match")

        user = User(
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password_confirm"),
        )
        password_validators = [
            MinimumLengthValidator(),
            UserAttributeSimilarityValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator(),
        ]

        try:
            validate_password(
                password=self.cleaned_data["password_confirm"],
                user=user,
                password_validators=password_validators,
            )
        except ValidationError as e:
            logger.error("validation failed")
            raise ValidationError(e)
        return self.cleaned_data["password_confirm"]

    def save(self, user, commit=True):
        user.set_password(self.cleaned_data["password_new"])
        user.save()
        return user


class GetEmailForm(forms.Form):
    email = forms.EmailField(label="email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        r = get_user_model().objects.filter(email=email)
        if r.count() == 0:
            raise ValidationError("Email doesn't exists")
        return email


class UserPreferenceForm(forms.Form):
    CHOICES_CATEGORY = [
        ("newamerican", "newamerican"),
        ("armenian", "armenian"),
        ("barbeque", "barbeque"),
        ("bars", "bars"),
        ("bistros", "bistros"),
        ("burgers", "burgers"),
        ("chinese", "chinese"),
        ("danish", "danish"),
        ("diners", "diners"),
        ("ethiopian", "ethiopian"),
        ("filipino", "filipino"),
        ("french", "french"),
        ("georgian", "georgian"),
        ("german", "german"),
        ("greek", "greek"),
        ("hotdog", "hotdog"),
        ("italian", "italian"),
        ("bistros", "bistros"),
        ("japanese", "japanese"),
        ("jewish", "jewish"),
        ("kebab", "kebab"),
        ("korean", "korean"),
        ("kosher", "kosher"),
        ("mexican", "mexican"),
        ("noodles", "noodles"),
        ("pizza", "pizza"),
        ("salad", "salad"),
        ("sandwiches", "sandwiches"),
        ("seafood", "seafood"),
        ("sushi", "sushi"),
        ("tapassmallplates", "tapassmallplates"),
        ("vegan", "vegan"),
        ("vegetarian", "vegetarian"),
        ("vietnamese", "vietnamese"),
        ("waffles", "waffles"),
        ("wraps", "wraps"),
    ]
    pref_list = forms.MultipleChoiceField(
        label="pref_list", choices=CHOICES_CATEGORY, required=False
    )

    def save(self, user, commit=True):
        category_list = self.cleaned_data.get("pref_list")
        for category in category_list:
            user.preferences.add(Categories.objects.get(category=category))
