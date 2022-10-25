from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.date import today_ymd

from systextil.models import Estagio

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
        ('', "Todos"),
        ('1', "1"),
        ('2', "2"),
        ('3', "3"),
        ('4', "4"),
    ]
    turno = forms.ChoiceField(
        choices=CHOICES,
        required=False,
        initial='',
    )

    estagio = forms.ModelChoiceField(
        label='Estágio',
        queryset=Estagio.objects.filter(codigo_estagio__gte=70).order_by(
            'codigo_estagio'
        ),
        required=False,
        empty_label="Todos",
        initial=76,
    )
