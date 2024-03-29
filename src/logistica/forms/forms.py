from datetime import datetime, timedelta
from pprint import pprint

from django import forms

from utils.functions import shift_years

from logistica.models import (
    NfEntrada,
    PosicaoCarga,
)


class NotafiscalChaveForm(forms.Form):
    chave = forms.CharField(
        widget=forms.TextInput())


class NotafiscalRelForm(forms.Form):

    def data_ini():
        return (datetime.now().replace(day=1)-timedelta(days=1)).replace(day=1)

    data_de = forms.DateField(
        label='Data do Faturamento: De',
        initial=data_ini,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    uf = forms.CharField(
        label='UF', max_length=2, min_length=2, required=False,
        widget=forms.TextInput(attrs={'size': 2}))

    nf = forms.CharField(
        label='Número da NF', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    transportadora = forms.CharField(
        label='Transportadora', required=False,
        help_text='Sigla da transportadora.',
        widget=forms.TextInput())

    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput())

    pedido = forms.CharField(
        label='Pedido Tussor', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    ped_cliente = forms.CharField(
        label='Pedido de cliente', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('N', 'Não filtra'),
               ('C', 'Com data de saída informada'),
               ('S', 'Sem data de saída')]
    data_saida = forms.ChoiceField(
        label='Quanto a data de saída', choices=CHOICES, initial='S')

    CHOICES = [('T', 'Todos (Sim ou Não)'),
               ('S', 'Sim'),
               ('N', 'Não')]
    entregue = forms.ChoiceField(
        choices=CHOICES, initial='T')

    CHOICES = [('N', 'Data base, empresa e NF (decrescente)'),
               ('P', 'Número do pedido (crescente)'),
               ('A', 'Atraso (maior primeiro)')]
    ordem = forms.ChoiceField(
        label='Ordem de apresentação', choices=CHOICES, initial='A')

    CHOICES = [('V', 'Apenas NF de venda e ativas (não canceladas)'),
               ('T', 'Totas as notas fiscais')]
    listadas = forms.ChoiceField(
        label='Notas listadas', choices=CHOICES, initial='V')

    posicao = forms.ModelChoiceField(
        label='Posição', required=False,
        queryset=PosicaoCarga.objects.all().order_by('id'),
        empty_label='--Todas--')

    CHOICES = [('-', 'Todas'),
               ('a', 'Atacado'),
               ('v', 'Varejo'),
               ('o', 'Outras')]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='-')

    por_pagina = forms.IntegerField(
        label='NF por página', required=True, initial=100,
        widget=forms.TextInput(attrs={'type': 'number'}))

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_uf(self):
        uf = self.cleaned_data['uf'].upper()
        data = self.data.copy()
        data['uf'] = uf
        self.data = data
        return uf

    def clean_data_de(self):
        data_de = self.cleaned_data['data_de']
        if data_de:
            if data_de.year < 100:
                data_de = shift_years(2000, data_de)
        return data_de


class NfPosicaoForm(forms.Form):
    data = forms.DateField(
        label='Data de movimento da carga',
        help_text='Só pode ficar vazia de posição form "Entregue ao apoio".',
        initial=datetime.now(), required=False,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))

    posicao = forms.ModelChoiceField(
        label='Posição', required=False,
        queryset=PosicaoCarga.objects.all().order_by('id'),
        initial=2, empty_label='--Todas--')


class EntradaNfForm(forms.ModelForm):

    cadastro = forms.CharField(
        label='CNPJ',
        widget=forms.TextInput(
            attrs={'size': 20, 'autofocus': 'autofocus'}))

    emissor = forms.CharField(
        widget=forms.TextInput(attrs={'size': 80}))

    descricao = forms.CharField(
        widget=forms.TextInput(attrs={'size': 80}))

    transportadora = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}))

    motorista = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}))


class EntradaNfSemXmlForm(EntradaNfForm):

    class Meta:
        model = NfEntrada
        fields = [
            'cadastro', 'numero', 'emissor', 'descricao', 'volumes',
            'chegada', 'transportadora', 'motorista', 'placa',
            'responsavel'
        ]

class ListaForm(forms.Form):
    numero = forms.CharField(
        label='Número da NF', required=False,
        widget=forms.TextInput(attrs={
            'type': 'number',
            'size': 8,
            'autofocus': 'autofocus',
        }))
    data = forms.DateField(
        label='Data de chegada', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    pagina = forms.IntegerField(
        required=False, widget=forms.HiddenInput())
