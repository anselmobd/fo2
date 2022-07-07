from pprint import pprint

from django import forms

__all__ = ['NfForm']


class NfForm(forms.Form):
    nf = forms.CharField(
        label='Número da NF', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
