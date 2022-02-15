import datetime
from pprint import pprint

from django import forms

from systextil.models import Familia


class PorCelulaForm(forms.Form):
    data_de = forms.DateField(
        label='Data de',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        # initial=datetime.date.today,
    )

    data_ate = forms.DateField(
        label='Até',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date'}
        ),
    )

    celula = forms.ModelChoiceField(
        label='Célula',
        required=False,
        queryset=Familia.objects.filter(
            divisao_producao__range=['1000', '9999']
        ).order_by(
            'divisao_producao'
        ),
        empty_label="(Todas)",
    )
