from django import forms

import geral


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

    CHOICES = [('999', '--Todos--')]
    depositos = geral.queries.deposito()
    for deposito in depositos:
        if deposito['COD'] > 1:
            CHOICES.append((
                deposito['COD'],
                '{} - {}'.format(deposito['COD'], deposito['DESCR'])
            ))
    deposito = forms.ChoiceField(
        label='Depósito', choices=CHOICES, initial='999')

    CHOICES = [('rct', 'Ref./Cor/Tamanho'),
               ('r', 'Referência')]
    agrupamento = forms.ChoiceField(
        choices=CHOICES, initial='rct')

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor
