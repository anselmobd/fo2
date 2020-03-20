from pprint import pprint

from django import forms

import geral.functions


class TransferenciaForm(forms.Form):
    string_upper_attrs = {
        'type': 'string',
        'style': 'text-transform:uppercase;',
        }

    autofocus_attrs = {
        'autofocus': 'autofocus;',
        }

    placeholder_00 = {
        'placeholder': '0...',
        }

    CHOICES = [
        ('1', '1 - Produtos confeccionados'),
        ('2', '2 - Tecidos acabados'),
        ('9', '9 - Materiais comprados'),
    ]
    nivel = forms.ChoiceField(
        label='Nível', required=True,
        choices=CHOICES, initial='1')

    ref = forms.CharField(
        label='Referência', required=True, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={
            **autofocus_attrs, **string_upper_attrs, **placeholder_00}))

    cor = forms.CharField(
        label='Cor', required=True, min_length=1, max_length=6,
        widget=forms.TextInput(attrs={
            **string_upper_attrs, **placeholder_00}))

    tam = forms.CharField(
        label='Tamanho', required=True, min_length=1, max_length=3,
        widget=forms.TextInput(attrs=string_upper_attrs))

    CHOICES = geral.functions.depositos_choices(only=(101, 102, 122, 231))

    deposito_origem = forms.ChoiceField(
        label='Depósito de origem', required=True,
        choices=CHOICES, initial='')

    deposito_destino = forms.ChoiceField(
        label='Depósito de destino', required=True,
        choices=CHOICES, initial='')

    def clean_ref(self):
        return self.cleaned_data['ref'].upper().zfill(5)

    def clean_cor(self):
        return self.cleaned_data['cor'].upper().zfill(6)

    def clean_tam(self):
        return self.cleaned_data['tam'].upper()
