from pprint import pprint

from django import forms

from systextil.models import Familia, Estagio
from utils.functions.date import today_ymd

class PorCelulaForm(forms.Form):
    data_de = forms.DateField(
        label='Data de',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'autofocus': 'autofocus'
            }
        ),
        initial=today_ymd,
    )

    data_ate = forms.DateField(
        label='Até',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date'}
        ),
    )

    celula = forms.ModelChoiceField(
        label='Célula célula',
        queryset=Familia.objects.filter(
            divisao_producao__range=['1000', '9999']
        ).order_by(
            'divisao_producao'
        ),
        initial=2836,
        required=False,
        empty_label='Qualquer',
    )

    estagio = forms.ModelChoiceField(
        label='Estágio',
        queryset=Estagio.objects.all().order_by(
            'codigo_estagio'
        ),
        initial=33,
    )
