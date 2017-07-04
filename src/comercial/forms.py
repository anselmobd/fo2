from django import forms


class ClienteForm(forms.Form):
    cnpj9 = forms.CharField(
        label='CNPJ-Inscrição (até 9 dígitos)',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    cnpj4 = forms.CharField(
        label='CNPJ-Filial (até 4 dígitos)',
        widget=forms.TextInput(attrs={'type': 'number'}))

    # nome = forms.CharField(
    #     label='Razão Social',
    #     required=False)
