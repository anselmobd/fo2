from pprint import pprint
from django import forms
# from django.core.exceptions import ValidationError

import geral.queries
import geral.functions
from base.forms import O2BaseForm, O2FieldRefForm
from base.forms.fields2 import O2FieldModeloForm2


class PorDepositoForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    ref = forms.CharField(
        label='Referência ou modelo',
        required=True, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string'}))

    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cor = forms.CharField(
        label='Cor', required=False, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))

    deposito = forms.ChoiceField(
        label='Depósito', initial='999')

    CHOICES = [
        ('rtcd', 'Referência/Tamanho/Cor/Depósito'),
        ('rctd', 'Referência/Cor/Tamanho/Depósito'),
        ('r', 'Referência/Depósito'),
        ('tc', 'Tamanho/Cor'),
        ('ct', 'Cor/Tamanho'),
        ('d', 'Depósito'),
    ]
    agrupamento = forms.ChoiceField(
        choices=CHOICES, initial='rtcd')

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

    def __init__(self, *args, cursor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.mount_choices()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            self.cursor,
            cod_todos='999', descr_todos='--Todos--', cod_only='A00',
            only=(101, 102, 103, 122, 231), rest=True)
        setattr(self.fields['deposito'], 'choices', CHOICES)

    def upper_clean(self, field_name):
        field = self.cleaned_data[field_name].upper()
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def clean_ref(self):
        return self.upper_clean('ref')

    def clean_tam(self):
        return self.upper_clean('tam')

    def clean_cor(self):
        return self.upper_clean('cor')


# def validate_nivel_mp(value):
#     if value != 2 and value != 9:
#         raise ValidationError(
#             '%(value)s não é nível de MP',
#             params={'value': value},
#         )


class ValorForm(forms.Form):
    # nivel = forms.IntegerField(
    #     label='Nível', required=False,
    #     help_text='2=Tecidos/malhas, 9=Demais materiais',
    #     validators=[validate_nivel_mp],
    #     widget=forms.TextInput(attrs={'type': 'number',
    #                            'autofocus': 'autofocus'}))
    CHOICES = [
        ('2', '2 - Tecidos/malhas'),
        ('9', '9 - Demais materiais'),
    ]
    nivel = forms.ChoiceField(
        label='Nível',
        choices=CHOICES, initial='a')

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


class InventarioExpedicaoForm(forms.Form):
    data_ini = forms.DateField(
        label='Referências com movimento a partir da data:',
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))


class ReferenciasEstoqueForm(
        O2BaseForm,
        O2FieldModeloForm2):

    deposito = forms.ChoiceField(
        label='Depósito', initial='-')

    def __init__(self, *args, cursor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.mount_choices()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            self.cursor,
            cod_todos='A00', only=(101, 102, 103, 122, 231))
        setattr(self.fields['deposito'], 'choices', CHOICES)

    class Meta:
        order_fields = ['deposito', 'modelo']
        autofocus_field = 'modelo'


class EditaEstoqueForm(forms.Form):
    qtd = forms.CharField(
        label='Quantidade inventariada', max_length=6, min_length=1,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    data = forms.DateField(
        label='Data do inventário', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    hora = forms.TimeField(
        label='Hora do inventário', required=False,
        help_text='Padrão: início do dia',
        widget=forms.TimeInput(attrs={'type': 'time'}))


class MostraEstoqueForm(forms.Form):
    qtd = forms.CharField(
        label='Quantidade inventariada',
        max_length=6, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    data = forms.DateField(
        label='Data do inventário', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    hora = forms.TimeField(
        label='Hora do inventário', required=False,
        help_text='Padrão: início do dia',
        widget=forms.TimeInput(attrs={'type': 'time'}))


class ConfrontaEstoqueForm(forms.Form):
    ref = forms.CharField(
        label='Referência ou modelo',
        required=False, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cor = forms.CharField(
        label='Cor', required=False, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))

    deposito = forms.ChoiceField(
        label='Depósito', required=True, initial='')

    def __init__(self, *args, cursor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.mount_choices()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            self.cursor,
            only=(101, 102, 103, 122, 231))
        setattr(self.fields['deposito'], 'choices', CHOICES)

    def upper_clean(self, field_name):
        field = self.cleaned_data[field_name].upper()
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def clean_ref(self):
        return self.upper_clean('ref')

    def clean_tam(self):
        return self.upper_clean('tam')

    def clean_cor(self):
        return self.upper_clean('cor')


class EstoqueNaDataForm(forms.Form):
    ref = forms.CharField(
        label='Referência ou modelo',
        required=True, min_length=1, max_length=5,
        widget=forms.TextInput(
            attrs={'type': 'string', 'autofocus': 'autofocus'}))

    cor = forms.CharField(
        label='Cor', required=False, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))

    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    data = forms.DateField(
        label='Data', required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}))

    hora = forms.TimeField(
        label='Hora', required=False,
        help_text='Padrão: início do dia',
        widget=forms.TimeInput(attrs={'type': 'time'}))

    deposito = forms.ChoiceField(
        label='Depósito', required=True, initial='')

    def __init__(self, *args, cursor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.mount_choices()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            self.cursor,
            cod_only='A00', only=(101, 102, 103, 122, 231))
        setattr(self.fields['deposito'], 'choices', CHOICES)

    def upper_clean(self, field_name):
        field = self.cleaned_data[field_name].upper()
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def clean_ref(self):
        return self.upper_clean('ref')

    def clean_cor(self):
        return self.upper_clean('cor')

    def clean_tam(self):
        return self.upper_clean('tam')
