from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.date import today_ymd


class OtPesarForm(forms.Form):
    a = FormWidgetAttrs()

    periodo = forms.CharField(
        label='Período',
        required=False,
        widget=forms.TextInput(
            attrs={
                **a.autofocus,
                **a.number,
                'size': 4,
            }
        )
    )

    data = forms.DateField(
        label="Data dentro do período",
        required=False,
        initial=today_ymd,
        widget=forms.DateInput(
            attrs={
                **a.date,
            }
        ),
    )
