from pprint import pprint

from django import forms


class DistribuicaoForm(forms.Form):
    modelo = forms.CharField(
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'number',
                'placeholder': '0',
            }
        )
    )
