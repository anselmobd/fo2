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

    vol_inicial = forms.CharField(
        label='Caixa inicial',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.number,
            }
        )
    )

    vol_final = forms.CharField(
        label='Caixa final',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.number,
            }
        )
    )
