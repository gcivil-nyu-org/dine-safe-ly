from .models import UserQuestionnaire
from django import forms


class QuestionnaireForm(forms.Form):
    restaurant_business_id = forms.CharField(label="restaurant_id")
    safety_level = forms.CharField(label="safety_level")

    temperature_required = forms.CharField(label="body_temp")
    contact_info_required = forms.CharField(label="contact_info")
    employee_mask = forms.CharField(label="employee_mask")
    capacity_compliant = forms.CharField(label="capacity")
    distance_compliant = forms.CharField(label="distance")

    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
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
            restaurant_business_id=self.cleaned_data.get("restaurant_business_id"),
            safety_level=self.cleaned_data.get("safety_level"),
            temperature_required=self.cleaned_data.get("temperature_required"),
            contact_info_required=self.cleaned_data.get("contact_info_required"),
            employee_mask=self.cleaned_data.get("employee_mask"),
            capacity_compliant=self.cleaned_data.get("capacity_compliant"),
            distance_compliant=self.cleaned_data.get("distance_compliant"),
        )
        return questionnaire
