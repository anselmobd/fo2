from pprint import pprint

from django import forms


class Add1PaleteForm(forms.Form):
    CHOICES = [
        ('PLT', 'Palete padrão'),
        ('CALHA', 'Palete da calha'),
        ('FANTAS', 'Palete fantasma'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='P')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

