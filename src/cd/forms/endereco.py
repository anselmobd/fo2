from pprint import pprint

from django import forms


class EnderecoForm(forms.Form):
    CHOICES = [
        ('TO', 'Todos'),
        ('ES', 'Estantes'),
        ('IN', 'Internos'),
        ('EX', 'Externos'),
        ('A', 'Estante A'),
        ('B', 'Estante B'),
        ('C', 'Estante C'),
        ('D', 'Estante D'),
        ('E', 'Estante E'),
        ('F', 'Estante F'),
        ('G', 'Estante G'),
        ('H', 'Estante H'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='ES')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())
