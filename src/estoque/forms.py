from django import forms
from django.core.exceptions import ValidationError

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

    CHOICES = [('rct', 'Referência/Tamanho/Cor/Depósito'),
               ('r', 'Referência/Depósito')]
    agrupamento = forms.ChoiceField(
        choices=CHOICES, initial='rct')

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='t')

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


def validate_nivel_mp(value):
    if value != 2 and value != 9:
        raise ValidationError(
            '%(value)s não é nível de MP',
            params={'value': value},
        )


class ValorForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', required=False,
        help_text='2=Tecidos/malhas, 9=Demais materiais',
        validators=[validate_nivel_mp],
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    positivos = forms.ChoiceField(
        label='Quantidade positiva',
        choices=CHOICES, initial='s')

    zerados = forms.ChoiceField(
        label='Quantidade zerada',
        choices=CHOICES, initial='n')

    negativos = forms.ChoiceField(
        label='Quantidade negativa',
        choices=CHOICES, initial='n')

    preco_zerado = forms.ChoiceField(
        label='Preço zerado',
        choices=CHOICES, initial='n')

    CHOICES = [
        ('a', 'Apenas os depósitos indicados pelo Compras'),
        ('t', 'Todos os depósitos'),
    ]
    deposito_compras = forms.ChoiceField(
        label='Quanto aos depósitos',
        choices=CHOICES, initial='a')
