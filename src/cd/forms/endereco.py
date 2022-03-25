from pprint import pprint

from django import forms


class EnderecoForm(forms.Form):
    CHOICES = [
        ('TO', 'Todos'),
        ('ES', 'Internos - Estantes (gera)'),
        ('NE', 'Internos - não Estantes'),
        ('IN', 'Internos - Todos'),
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


class EnderecoImprimeForm(forms.Form):
    inicial = forms.CharField(
        max_length=9, min_length=3,
        widget=forms.TextInput(attrs={
            'style': 'text-transform:uppercase;',
            'autofocus': 'autofocus',
        })
    )
    final = forms.CharField(
        max_length=9, min_length=3,
        widget=forms.TextInput(attrs={
            'style': 'text-transform:uppercase;',
        })
    )
