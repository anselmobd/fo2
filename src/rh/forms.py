from pprint import pprint
from django import forms


class SugestaoForm(forms.Form):
    number_attrs = {
        'type': 'number;',
        }

    autofocus_attrs = {
        'autofocus': 'autofocus;',
        }

    codigo = forms.CharField(
        label='Código (matrícula)',
        required=True, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={
            **autofocus_attrs, **number_attrs}))
