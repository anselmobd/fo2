from pprint import pprint

from django import forms

from utils.functions.date import yesterday_ymd


__all__ = ['GeraPedidoOpForm']


class GeraPedidoOpForm(forms.Form):
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
