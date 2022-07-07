from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs

__all__ = ['NfForm']


class NfForm(forms.Form):
    a = FormWidgetAttrs()

    nf = forms.CharField(
        label='Número da NF',
        widget=forms.TextInput(
            attrs={
                'size': 6,
                **a.number,
                **a.autofocus,
            }
        )
    )
