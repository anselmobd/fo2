from django import forms


class PorDepositoForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    ref = forms.CharField(
        label='Referência', max_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', max_length=6, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
