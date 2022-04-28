from pprint import pprint

from django import forms

from systextil.models import Familia, Estagio
from utils.functions.date import yesterday_ymd

class RomaneioCorteForm(forms.Form):
    data = forms.DateField(
        label='Data',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        initial=yesterday_ymd,
    )
    CHOICES = [
        ('n', 'Gera pedidos para NF (OPs completadas no estágio 16 na data)'),
        ('c', 'Visualiza OPs completadas no estágio 16 na data'),
        ('p', 'Visualiza a produção do estágio 16 na data'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES,
        initial='n',
    )
