from django import forms
from .models import TrackedCard


class TrackedCardForm(forms.ModelForm):
    class Meta:
        # Which model this form is for
        model = TrackedCard

        # Which fields show up on the form (user and dates are handled automatically)
        fields = ['card_name', 'card_set', 'card_year', 'grade_tier', 'status', 'notes']

        # Customize how each field looks in HTML
        widgets = {
            'card_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Charizard',
            }),
            'card_set': forms.TextInput(attrs={
                'placeholder': 'e.g. Base Set',
            }),
            'card_year': forms.NumberInput(attrs={
                'placeholder': 'e.g. 2025',
                'min': 1996,
                'max': 2027,
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Any notes about this card...',
                'rows': 3,
            }),
        }