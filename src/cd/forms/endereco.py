from pprint import pprint

from django import forms


class EnderecoForm(forms.Form):
    CHOICES = [
        ('T', 'Todos'),
        ('E', 'Estante'),
        ('I', 'Internos'),
        ('X', 'Externos'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='E')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())
