from pprint import pprint

from django import forms


class PorCelulaForm(forms.Form):
    data_de = forms.DateField(
        label='Data de',
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
