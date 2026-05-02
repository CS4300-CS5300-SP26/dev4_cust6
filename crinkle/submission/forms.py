from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            "card_name",
            "grading_service",
            "full_name",
            "address",
            "city",
            "state",
            "zip_code",
            "card_number",
            "expiry",
            "cvv",
        ]
        widgets = {
            "card_name": forms.TextInput(
                attrs={"placeholder": "Card name"}
            ),
            "grading_service": forms.Select(),
            "full_name": forms.TextInput(
                attrs={"placeholder": "Full name"}
            ),
            "address": forms.TextInput(
                attrs={"placeholder": "Street address"}
            ),
            "city": forms.TextInput(
                attrs={"placeholder": "City"}
            ),
            "state": forms.TextInput(
                attrs={"placeholder": "State"}
            ),
            "zip_code": forms.TextInput(
                attrs={"placeholder": "ZIP code"}
            ),
            "card_number": forms.TextInput(
                attrs={"placeholder": "1234 5678 9012 3456"}
            ),
            "expiry": forms.TextInput(
                attrs={"placeholder": "MM/YY"}
            ),
            "cvv": forms.TextInput(
                attrs={"placeholder": "CVV"}
            ),
        }