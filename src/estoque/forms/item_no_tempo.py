from pprint import pprint

from django import forms

import geral.functions


class ItemNoTempoForm(forms.Form):

    string_upper_attrs = {
        'type': 'string',
        'style': 'text-transform:uppercase;',
        }

    autofocus_attrs = {
        'autofocus': 'autofocus;',
        }

    ref = forms.CharField(
        label='Referência',
        required=True, min_length=5, max_length=5,
        widget=forms.TextInput(attrs={
            **autofocus_attrs, **string_upper_attrs}))

    cor = forms.CharField(
        label='Cor', required=True, max_length=6,
        widget=forms.TextInput(attrs=string_upper_attrs))

    tam = forms.CharField(
        label='Tamanho', required=True, min_length=1, max_length=3,
        widget=forms.TextInput(attrs=string_upper_attrs))

    deposito = forms.ChoiceField(
        label='Depósito', required=True,
        initial='')

    CHOICES = [
        ('1', '1 Mês'),
        ('3', '3 Meses'),
        ('6', '6 Meses'),
        ('0', 'Todo o histórico disponível'),
    ]
    periodo = forms.ChoiceField(
        label='Período', required=True,
        choices=CHOICES, initial='3')

    CHOICES = [
        ('S', 'Sim'),
        ('N', 'Não'),
    ]
    agrupa = forms.ChoiceField(
        label='Agrupa transações', required=True,
        choices=CHOICES, initial='S')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount_choices()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            only=(101, 102, 103, 122, 231), rest=True)
        setattr(self.fields['deposito'], 'choices', CHOICES)

    def clean_ref(self):
        return self.cleaned_data['ref'].upper()

    def clean_cor(self):
        return self.cleaned_data['cor'].upper().zfill(6)

    def clean_tam(self):
        return self.cleaned_data['tam'].upper()
