from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.date import today_ymd

__all__ = ['Form']


class Form(forms.Form):
    a = FormWidgetAttrs()

    data_de = forms.DateField(
        label="Data de emissão do pedido: De",
        initial=today_ymd,
        widget=forms.DateInput(
            attrs={
                **a.date,
                **a.autofocus,
            }
        ),
    )

    data_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    CHOICES = [
        ('', "--Não filtra--"),
        ('s', "Sim"),
        ('n', "Não"),
    ]
    faturado = forms.ChoiceField(
        choices=CHOICES,
        required=False,
        initial='',
    )
