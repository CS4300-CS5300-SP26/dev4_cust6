from django import forms
from .models import CardCollection


class CollectionSettingsForm(forms.ModelForm):
    class Meta:
        model = CardCollection
        fields = [
            "sort_order",
            "value_threshold",
        ]

        widgets = {
            "sort_order": forms.Select(attrs={"class": "input-field"}),
            "value_threshold": forms.NumberInput(attrs={"class": "input-field"}),
        }
