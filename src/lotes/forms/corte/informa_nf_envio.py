from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs


class InformaNfEnvioForm(forms.Form):
    a = FormWidgetAttrs()

    nf = forms.CharField(
        label='Nota fiscal',
        widget=forms.TextInput(
            attrs={
                **a.string,
                **a.autofocus,
            }
        )
    )
