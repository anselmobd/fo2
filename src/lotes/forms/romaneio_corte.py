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
        ('n', 'OPs completadas no estágio 16 na data; para NF'),
        ('c', 'OPs completadas no estágio 16 na data'),
        ('p', 'Produção do estágio 16 na data'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES,
        initial='n',
    )
