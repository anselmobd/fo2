from pprint import pprint

from django import forms

from o2.forms.custom import FormWidgetAttrs


class SugestaoForm(forms.Form):
    a = FormWidgetAttrs()

    codigo = forms.CharField(
        label='Código (matrícula)',
        required=True, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={
            **a.autofocus, **a.number}))
