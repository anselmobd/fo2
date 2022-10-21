from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.date import today_ymd

__all__ = ['Form']


class Form(forms.Form):
    a = FormWidgetAttrs()

    data_de = forms.DateField(
        label="Data inicial",
        initial=today_ymd,
        widget=forms.DateInput(
            attrs={
                **a.date,
                **a.autofocus,
            }
        ),
    )

    data_ate = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="(se não definida, considerada igual a inicial)"
    )

    CHOICES = [
        ('-', "Todos"),
        ('1', "1 - 18h às 6h"),
        ('2', "2 - 6h às 18h"),
        ('3', "3 - 18h às 6h"),
        ('4', "4 - 6h às 18h"),
    ]
    turno = forms.ChoiceField(
        choices=CHOICES,
        initial='-',
    )
