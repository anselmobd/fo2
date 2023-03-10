from pprint import pprint

from django import forms

from utils.functions.date import yesterday_ymd


class PedidosGeradosForm(forms.Form):
    data = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        initial=yesterday_ymd,
    )
