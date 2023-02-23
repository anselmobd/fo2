from pprint import pprint

from django import forms

from systextil.models import Familia, Estagio
from utils.functions.date import yesterday_ymd

class RomaneioOpCortadaForm(forms.Form):
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
