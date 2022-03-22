from pprint import pprint

from django import forms

from systextil.models import Familia, Estagio
from utils.functions.date import today_ymd

class RomaneioCorteForm(forms.Form):
    data = forms.DateField(
        label='Data',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        initial=today_ymd,
    )
    CHOICES = [
        ('c', 'OPs completadas no estágio 16 na data'),
        ('n', 'OPs completadas no estágio 16 na data; para NF'),
        ('p', 'Produção do estágio 16 na data'),
    ]
    tipo = forms.ChoiceField(
        choices=CHOICES,
        initial='c',
    )
