from pprint import pprint

from django import forms


class EnderecoForm(forms.Form):
    CHOICES = [
        ('TO', 'Todos'),
        ('ES', 'Estante'),
        ('IN', 'Internos'),
        ('EX', 'Externos'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='ES')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())
