import datetime
from pprint import pprint

from django import forms

import geral.functions

import estoque.models


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
            'size': 5,
            **autofocus_attrs, **string_upper_attrs, **placeholder_00}))

    cor = forms.CharField(
        label='Cor', required=True, min_length=1, max_length=6,
        widget=forms.TextInput(attrs={
            'size': 6, **string_upper_attrs, **placeholder_00}))

    tam = forms.CharField(
        label='Tamanho', required=True, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={
            'size': 3, **string_upper_attrs}))

    qtd = forms.IntegerField(
        label='Quantidade',
        widget=forms.TextInput(attrs={'size': 6, 'type': 'number'}))

    CHOICES = geral.functions.depositos_choices(only=(101, 102, 122, 231))

    deposito_origem = forms.ChoiceField(
        label='Depósito de origem', required=True,
        choices=CHOICES, initial='231')

    deposito_destino = forms.ChoiceField(
        label='Depósito de destino', required=True,
        choices=CHOICES, initial='122')

    num_doc = forms.ChoiceField(
        label='Número de documento', required=False,
        choices=[], initial=0)

    descricao = forms.CharField(
        label='Descrição do documento', required=False,
        widget=forms.TextInput(attrs={'size': 50}))

    def __init__(self, *args, user=None, **kwargs):
        super(TransferenciaForm, self).__init__(*args, **kwargs)

        self.user = user
        self.mount_num_doc_choices()

    def mount_num_doc_choices(self):
        self.num_doc_recente = 0
        novo = [
            {'numero': 0,
             'descricao': "Cria novo número de documento",
             }]
        obj_docs = estoque.models.DocMovStq.objects.filter(
            usuario=self.user, data=datetime.date.today()).order_by(
                '-id')
        docs = []
        for doc in obj_docs:
            if self.num_doc_recente == 0:
                self.num_doc_recente = doc.num_doc
            docs.append({
                'numero': doc.num_doc,
                'descricao': str(doc),
            })

        CHOICES = []
        for num in (novo + docs):
            CHOICES.append((
                num['numero'],
                num['descricao'],
            ))

        self.fields['num_doc'].choices = CHOICES
        self.fields['num_doc'].initial = self.num_doc_recente

    def clean_ref(self):
        return self.cleaned_data['ref'].upper().zfill(5)

    def clean_cor(self):
        return self.cleaned_data['cor'].upper().zfill(6)

    def clean_tam(self):
        return self.cleaned_data['tam'].upper()

    def clean_qtd(self):
        qtd = self.cleaned_data['qtd']
        if qtd <= 0:
            raise forms.ValidationError(
                    "Quantidade deve ser maior que zero.")
        return qtd
