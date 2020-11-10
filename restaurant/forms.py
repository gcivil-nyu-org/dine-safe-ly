from .models import UserQuestionnaire
from django import forms


class QuestionnaireForm(forms.Form):
    restaurant_business_id = forms.CharField(label="restaurant_id")
    user_id = forms.CharField(label="user_id")
    safety_level = forms.CharField(label="safety_level")
    saved_on = forms.DateTimeField(required=False, label="saved_on")

    temperature_required = forms.CharField(label="body_temp_required")
    contact_info_required = forms.CharField(label="contact_info")
    employee_mask = forms.CharField(label="employee_mask")
    capacity_compliant = forms.CharField(label="capacity")
    distance_compliant = forms.CharField(label="distance")

    def save(self, commit=True):
        questionnaire = UserQuestionnaire.objects.create(
            restaurant_business_id=self.cleaned_data.get("restaurant_business_id"),
            user_id=self.cleaned_data.get("user_id"),
            safety_level=self.cleaned_data.get("safety_level"),
            temperature_required=self.cleaned_data.get("temperature_required"),
            contact_info_required=self.cleaned_data.get("contact_info_required"),
            employee_mask=self.cleaned_data.get("employee_mask"),
            capacity_compliant=self.cleaned_data.get("capacity_compliant"),
            distance_compliant=self.cleaned_data.get("distance_compliant"),
        )
        return questionnaire


class SearchFilterForm(forms.Form):
    CHOICES_NEIGHBOURHOOD = [
        ("Southwest Queens", "Southwest Queens "),
        ("Rockaways", "Rockaways ")
    ]
    CHOICES_CATEGORY = []
    CHOICES_COMPLIANCE = [('All', 'All'), ('Compliant', 'Compliant')]

    keyword = forms.CharField(label="keyword", required=False)
    neighbourhood = forms.MultipleChoiceField(label="neighbourhood", choices=CHOICES_NEIGHBOURHOOD, required=False)
    category = forms.MultipleChoiceField(label="category", choices=CHOICES_CATEGORY, required=False)
    price_1 = forms.BooleanField(label="price_1", required=False)
    price_2 = forms.BooleanField(label="price_2", required=False)
    price_3 = forms.BooleanField(label="price_3", required=False)
    price_4 = forms.BooleanField(label="price_4", required=False)

    All = forms.ChoiceField(label="All", widget=forms.RadioSelect, choices=CHOICES_COMPLIANCE, required=False)
    Compliant = forms.ChoiceField(label="Compliant", widget=forms.RadioSelect, choices=CHOICES_COMPLIANCE, required=False)

    slider_snap_input_from = forms.CharField(label="slider_snap_input_from", required=False)
    slider_snap_input_to = forms.CharField(label="slider_snap_input_to", required=False)

    def clean_keyword(self):
        keyword = self.cleaned_data.get('keyword')
        if keyword == "":
            return None
        return keyword

    def clean_neighbourhood(self):
        neighbourhood = self.cleaned_data.get('neighbourhood')
        # Check if Empty list
        if neighbourhood is not None and len(neighbourhood) == 0:
            return None
        return neighbourhood

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category is not None and len(category) == 0:
            return None
        return category

    def get_price_filter(self):
        price_filter = []
        if self.cleaned_data.get('price_1'):
            price_filter.append(self.cleaned_data.get('price_1'))
        if self.cleaned_data.get('price_2'):
            price_filter.append(self.cleaned_data.get('price_2'))
        if self.cleaned_data.get('price_3'):
            price_filter.append(self.cleaned_data.get('price_3'))
        if self.cleaned_data.get('price_4'):
            price_filter.append(self.cleaned_data.get('price_4'))
        return price_filter

    def get_rating_filter(self):
        rating_filter = []
        if self.cleaned_data.get('slider_snap_input_from'):
            rating_filter.append(self.cleaned_data.get('slider_snap_input_from'))
        if self.cleaned_data.get('slider_snap_input_to'):
            rating_filter.append(self.cleaned_data.get('slider_snap_input_to'))
        return rating_filter
        

