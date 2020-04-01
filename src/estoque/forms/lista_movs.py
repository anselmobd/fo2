from pprint import pprint

from django import forms


class ListaMovimentosForm(forms.Form):
    num_doc = forms.IntegerField(
        label='Número de documento',
        widget=forms.TextInput(attrs={
            'type': 'number', 'size': 9, 'autofocus': 'autofocus'}))
