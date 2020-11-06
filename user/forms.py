from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError


class UserCreationForm(forms.Form):
    username = forms.CharField(label="Enter Username", min_length=4, max_length=150)
    email = forms.EmailField(label="Enter email")
    password1 = forms.CharField(label="Enter password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
        )
        return user


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label="password1", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password2", widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, uid, commit=True):
        user = User.objects.get(pk=uid)
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

        return password2

    def save(self, user, commit=True):
        user.set_password(self.cleaned_data["password_new"])
        user.save()
        return user


class GetEmailForm(forms.Form):
    email = forms.EmailField(label="email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        r = User.objects.filter(email=email)
        if r.count() == 0:
            raise ValidationError("Email doesn't exists")
        return email
