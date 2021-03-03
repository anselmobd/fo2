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

    placeholder_00_00 = {
        'placeholder': '0... 0... ...',
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

    cores = forms.CharField(
        label='Cores', required=True, min_length=1,
        widget=forms.TextInput(attrs={
            **string_upper_attrs, **placeholder_00_00}))

    tam = forms.CharField(
        label='Tamanho', required=True, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={
            'size': 3, **string_upper_attrs}))

    qtd = forms.IntegerField(
        label='Quantidade',
        widget=forms.TextInput(attrs={'size': 6, 'type': 'number'}))

    deposito_origem = forms.ChoiceField(
        label='Depósito de origem', required=True,
        initial='102')

    deposito_destino = forms.ChoiceField(
        label='Depósito de destino', required=True,
        initial='122')

    nova_ref = forms.CharField(
        label='Nova referência', required=False, max_length=5,
        widget=forms.TextInput(attrs={
            'size': 5, **string_upper_attrs, **placeholder_00}))

    nova_cor = forms.CharField(
        label='Nova cor', required=False, max_length=6,
        widget=forms.TextInput(attrs={
            'size': 6, **string_upper_attrs, **placeholder_00}))

    novas_cores = forms.CharField(
        label='Novas cores', required=True, min_length=1,
        widget=forms.TextInput(attrs={
            **string_upper_attrs, **placeholder_00_00}))

    novo_tam = forms.CharField(
        label='Novo tamanho', required=False, max_length=3,
        widget=forms.TextInput(attrs={
            'size': 3, **string_upper_attrs}))

    num_doc = forms.ChoiceField(
        label='Número de documento', required=False,
        choices=[], initial=0)

    descricao = forms.CharField(
        label='Descrição do documento', required=False,
        widget=forms.TextInput(attrs={'size': 50}))

    def __init__(self, *args, cursor=None, user=None, tipo_mov=None, **kwargs):
        super(TransferenciaForm, self).__init__(*args, **kwargs)

        self.cursor = cursor
        self.user = user
        self.tipo_mov = tipo_mov

        self.mount_choices()
        self.mount_num_doc_choices()
        self.hidden_fields()

    def mount_choices(self):
        CHOICES = geral.functions.depositos_choices(
            self.cursor,
            only=(101, 102, 103, 122, 231))
        setattr(self.fields['deposito_origem'], 'choices', CHOICES)
        setattr(self.fields['deposito_destino'], 'choices', CHOICES)

    def hidden_field(self, field):
        field.required = False
        field.initial = None
        field.widget = forms.HiddenInput()

    def hidden_fields(self):
        if self.tipo_mov.trans_entrada == 0:
            self.hidden_field(self.fields['deposito_destino'])
        if self.tipo_mov.trans_saida == 0:
            self.hidden_field(self.fields['deposito_origem'])
        if not self.tipo_mov.renomeia:
            self.hidden_field(self.fields['nova_ref'])
            self.hidden_field(self.fields['nova_cor'])
            self.hidden_field(self.fields['novo_tam'])
        if self.tipo_mov.unidade in ['D'] :
            self.hidden_field(self.fields['nova_cor'])
        if self.tipo_mov.unidade in ['1', 'D'] :
            self.hidden_field(self.fields['cores'])
        if self.tipo_mov.unidade in ['M'] :
            self.hidden_field(self.fields['cor'])
        if self.tipo_mov.unidade in ['1', 'M'] :
            self.hidden_field(self.fields['novas_cores'])

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

    def clean_ncores(self, field, descr):
        field_input = self.fields[field]
        cleaned = None
        if field_input.required:
            ncores = 0
            try:
                sep_chars = ",.;-_+"
                cores = self.cleaned_data[field].translate(
                    "".maketrans(sep_chars, " "*len(sep_chars)))

                cleaned = ''
                sep = ''
                cores = cores.split()
                for cor in cores:
                    if cor:
                        ncores += 1
                        cleaned += sep + cor.upper().zfill(6)
                        sep = ' '
            except Exception:
                cleaned = None
            if ncores < 2:
                raise forms.ValidationError(
                        f"{descr} deve conter pelo menos 2 cores.")
        return cleaned

    def clean_cores(self):
        return self.clean_ncores('cores', 'Cores')

    def clean_novas_cores(self):
        return self.clean_ncores('novas_cores', 'Novas cores')

    def clean_tam(self):
        return self.cleaned_data['tam'].upper()

    def clean_qtd(self):
        qtd = self.cleaned_data['qtd']
        if qtd <= 0:
            raise forms.ValidationError(
                    "Quantidade deve ser maior que zero.")
        return qtd

    def clean_nova_ref(self):
        cleaned = self.cleaned_data['nova_ref']
        if len(cleaned) == 0:
            return ''
        return cleaned.upper().zfill(5)

    def clean_nova_cor(self):
        cleaned = self.cleaned_data['nova_cor']
        if len(cleaned) == 0:
            return ''
        return cleaned.upper().zfill(6)

    def clean_novo_tam(self):
        return self.cleaned_data['novo_tam'].upper()
