from .models import UserQuestionnaire
from django import forms

# from django.core.exceptions import ValidationError


class QuestionnaireForm(forms.Form):
    # the restaurant the feedback is for
    restaurant_business_id = forms.CharField(label="restaurant_id")
    safety_level = forms.CharField(label="safety_level")

    temperature_required = forms.BooleanField(label="body_temp")
    contact_info_required = forms.BooleanField(label="contact_info")
    employee_mask = forms.BooleanField(label="employee_mask")
    capacity_compliant = forms.BooleanField(label="capacity")
    distance_compliant = forms.BooleanField(label="distance")

    def __str__(self):
        return "{} {} {} {} {} {}".format(
            self.restaurant_business_id,
            self.safety_level,
            self.temperature_required,
            self.contact_info_required,
            self.employee_mask,
            self.capacity_compliant,
            self.distance_compliant,
        )

    def save(self, commit=True):
        questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id=self.restaurant_business_id,
            safety_level=self.safety_level,
            temperature_required=self.temperature_required,
            contact_info_required=self.contact_info_required,
            employee_mask=self.employee_mask,
            capacity_compliant=self.capacity_compliant,
            distance_compliant=self.distance_compliant,
        )
        return questionnaire
