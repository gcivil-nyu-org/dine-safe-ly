from .models import UserQuestionnaire
from django import forms

# from django.core.exceptions import ValidationError


class QuestionnaireForm(forms.Form):
    # indicate your level or satisfaction for this restaurant
    satisfaction_level = forms.CharField(max_length=200)
    # indicate your level of safety for this restaurant
    safety_level = forms.CharField(max_length=200)
    mask_required = forms.CharField(max_length=200)
    temperature_required = forms.CharField(max_length=200)
    would_recommend = forms.CharField(max_length=200)

    def save(self, commit=True):
        questionnaire = UserQuestionnaire.objects.create_user(
            restaurant_business_id="",
            username="",
            email="",
            password="",
        )
        return questionnaire
