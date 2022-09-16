from pprint import pprint

from django import forms


class Add1PaleteForm(forms.Form):
    CHOICES = [
        ('PLT', 'Padrão'),
        ('CALHA', 'Calha'),
        ('FANTAS', 'Fantasma'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='P')
