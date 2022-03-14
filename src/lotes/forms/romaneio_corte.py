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
