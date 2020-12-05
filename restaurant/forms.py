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
        ("Chelsea and Clinton", "Chelsea and Clinton"),
        ("Lower East Side", "Lower East Side"),
        ("Gramercy Park and Murray Hill", "Gramercy Park and Murray Hill"),
        ("Greenwich Village and Soho", "Greenwich Village and Soho"),
        ("Upper West Side", "Upper West Side"),
        ("Central Harlem", "Central Harlem"),
        ("Upper East Side", "Upper East Side"),
        ("East Harlem", "East Harlem"),
        ("Inwood and Washington Heights", "Inwood and Washington Heights"),
        ("Lower Manhattan", "Lower Manhattan"),
        ("Stapleton and St. George", "Stapleton and St. George"),
        ("Tribeca", "Tribeca"),
        ("Port Richmond", "Port Richmond"),
        ("South Shore", "South Shore"),
        ("Mid-Island", "Mid-Island"),
        ("High Bridge and Morrisania", "High Bridge and Morrisania"),
        ("Central Bronx", "Central Bronx"),
        ("Hunts Point and Mott Haven", "Hunts Point and Mott Haven"),
        ("Bronx Park and Fordham", "Bronx Park and Fordham"),
        ("Southeast Bronx", "Southeast Bronx"),
        ("Northeast Bronx", "Northeast Bronx"),
        ("Kingsbridge and Riverdale", "Kingsbridge and Riverdale"),
        ("Southeast Queens", "Southeast Queens"),
        ("Northwest Queens", "Northwest Queens"),
        ("Long Island City", "Long Island City"),
        ("Northwest Brooklyn", "Northwest Brooklyn"),
        ("Bushwick and Williamsburg", "Bushwick and Williamsburg"),
        ("East New York and New Lots", "East New York and New Lots"),
        ("Southwest Brooklyn", "Southwest Brooklyn"),
        ("Flatbush", "Flatbush"),
        ("Greenpoint", "Greenpoint"),
        ("Central Brooklyn", "Central Brooklyn"),
        ("Borough Park", "Borough Park"),
        ("Sunset Park", "Sunset Park"),
        ("Bushwick and Williamsburg", "Bushwick and Williamsburg"),
        ("Southern Brooklyn", "Southern Brooklyn"),
        ("Canarsie and Flatlands", "Canarsie and Flatlands"),
        ("North Queens", "North Queens"),
        ("Northeast Queens", "Northeast Queens"),
        ("Central Queens", "Central Queens"),
        ("West Queens", "West Queens"),
        ("West Central Queens", "West Central Queens"),
        ("Southeast Queens", "Southeast Queens"),
        ("Jamaica", "Jamaica"),
        ("Southwest Queens", "Southwest Queens"),
        ("Rockaways", "Rockaways"),
    ]
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
    CHOICES_COMPLIANCE = [("All", "All"), ("Compliant", "Compliant")]
    CHOICES_RATING = [("5", "5"), ("4", "4"), ("3", "3"), ("2", "2"), ("1", "1")]

    CHOICES_SORT = [
        ("none", "none"),
        ("recommended", "recommended"),
        ("ratedhigh", "ratedhigh"),
        ("ratedlow", "ratedlow"),
        ("pricehigh", "pricehigh"),
        ("pricelow", "pricelow"),
    ]

    keyword = forms.CharField(label="keyword", required=False)
    neighbourhood = forms.MultipleChoiceField(
        label="neighbourhood", choices=CHOICES_NEIGHBOURHOOD, required=False
    )
    category = forms.MultipleChoiceField(
        label="category", choices=CHOICES_CATEGORY, required=False
    )

    form_sort = forms.ChoiceField(
        label="form_sort", choices=CHOICES_SORT, required=False
    )

    price_1 = forms.BooleanField(label="price_1", required=False)
    price_2 = forms.BooleanField(label="price_2", required=False)
    price_3 = forms.BooleanField(label="price_3", required=False)
    price_4 = forms.BooleanField(label="price_4", required=False)

    All = forms.ChoiceField(
        label="All",
        widget=forms.RadioSelect,
        choices=CHOICES_COMPLIANCE,
        required=False,
    )
    Compliant = forms.ChoiceField(
        label="All",
        widget=forms.RadioSelect,
        choices=CHOICES_COMPLIANCE,
        required=False,
    )

    fav = forms.BooleanField(label="fav", required=False)

    rating = forms.MultipleChoiceField(
        label="rating", choices=CHOICES_RATING, required=False
    )

    def clean_keyword(self):
        keyword = self.cleaned_data.get("keyword")
        if keyword == "":
            return None
        return keyword

    def clean_neighbourhood(self):
        neighbourhood = self.cleaned_data.get("neighbourhood")
        # Check if Empty list
        if neighbourhood is not None and len(neighbourhood) == 0:
            return None
        return neighbourhood

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category is not None and len(category) == 0:
            return None
        return category

    def get_price_filter(self):
        price_filter = []
        if self.cleaned_data.get("price_1"):
            price_filter.append("$")
        if self.cleaned_data.get("price_2"):
            price_filter.append("$$")
        if self.cleaned_data.get("price_3"):
            price_filter.append("$$$")
        if self.cleaned_data.get("price_4"):
            price_filter.append("$$$$")
        return price_filter

    def get_rating_filter(self):
        rating_filter = []
        if self.cleaned_data.get("rating"):
            for rating in self.cleaned_data.get("rating"):
                rating_filter.append(rating)
                rating_filter.append(str(float(rating) - 0.5))
        return rating_filter

    def get_compliant_filter(self):
        if self.cleaned_data.get("All") == "Compliant":
            return "Compliant"
        return None
