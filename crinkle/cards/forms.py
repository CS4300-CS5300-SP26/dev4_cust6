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
            "sort_order": forms.ChoiceField(
                choices=["name", "date_scanned", "grading_notes"]
            ),
            "value_threshold": forms.DecimalField(max_digits=12, decimal_places=2),
        }
