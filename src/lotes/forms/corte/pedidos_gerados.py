from pprint import pprint

from django import forms

from utils.functions.date import today_ymd


class PedidosGeradosForm(forms.Form):
    data = forms.DateField(
        label='Data de criação do pedido',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        required=False,
        initial=today_ymd,
    )
