from pprint import pprint

from django import forms


class EnderecoForm(forms.Form):
    CHOICES = [
        ('TO', 'Todos'),
        ('ES', 'Internos - Estantes (Gera)'),
        ('QA', 'Internos - Quarto andar (Gera)'),
        ('LA', 'Internos - Lateral (Gera)'),
        ('NG', 'Internos - não Gerados'),
        ('IN', 'Internos - Todos'),
        ('S', 'Externos - S (Gera)'),
        ('EX', 'Externos - não Gerados'),
        ('A', 'Interna - Estante A'),
        ('B', 'Interna - Estante B'),
        ('C', 'Interna - Estante C'),
        ('D', 'Interna - Estante D'),
        ('E', 'Interna - Estante E'),
        ('F', 'Interna - Estante F'),
        ('G', 'Interna - Estante G'),
        ('H', 'Interna - Estante H'),
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
