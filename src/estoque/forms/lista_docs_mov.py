from pprint import pprint

from django import forms


class ListaDocsMovimentacaoForm(forms.Form):
    data = forms.DateField(
        label='Data', required=False,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
