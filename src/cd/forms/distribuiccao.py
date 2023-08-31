from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs


class DistribuicaoForm(forms.Form):
    a = FormWidgetAttrs()

    modelo = forms.CharField(
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.number,
                **a.autofocus,
            }
        )
    )
