from pprint import pprint

from django import forms


class EnviaInsumoForm(forms.Form):
    dt_de = forms.DateField(
        label='Data emissão: De',
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date'})
    )

    dt_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(
            attrs={'type': 'date'})
    )
