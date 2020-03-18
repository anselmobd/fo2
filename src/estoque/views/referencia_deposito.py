from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import utils.functions.str
from utils.views import totalize_grouped_data, group_rowspan

import produto.queries

from estoque import forms
from estoque import queries


class ReferenciaDeposito(View):

    def __init__(self, *args, **kwargs):
        super(ReferenciaDeposito).__init__(*args, **kwargs)
        self.Form_class = forms.ReferenciasEstoqueForm
        self.template_name = 'estoque/referencia_deposito.html'
        self.context = {
            'titulo': 'Em depósito',
            'str_depositos': self.str_depositos(),
        }

    def mount_context(self, request, cursor, deposito, modelo):
        context = {
            'deposito': deposito,
            'modelo': modelo,
        }
        try:
            imodelo = int(modelo)
        except Exception:
            imodelo = None
        if imodelo is not None:
            anterior = None
            posterior = None
            get_prox = False
            lista = produto.queries.busca_modelo(cursor)
            for row in lista:
                item = row['modelo']
                if get_prox:
                    posterior = item
                    break
                else:
                    if imodelo == item:
                        get_prox = True
                    else:
                        anterior = item
            context.update({
                'anterior': anterior,
                'posterior': posterior,
            })

        data = queries.referencia_deposito(cursor, deposito, modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            row['ref|TARGET'] = '_blank'
            row['ref|LINK'] = reverse(
                'estoque:mostra_estoque__get', args=[
                    row['dep'], row['ref']])

        group = ['dep']
        tot_conf = {
            'group': group,
            'sum': ['estoque', 'falta', 'soma'],
            'count': [],
            'descr': {'ref': 'Totais:'},
        }
        if deposito == '-':
            tot_conf.update({
                'global_sum': ['estoque', 'falta', 'soma'],
                'global_descr': {'ref': 'Totais gerais:'},
            })
        totalize_grouped_data(data, tot_conf)
        group_rowspan(data, group)

        context.update({
            'headers': ['Depósito', 'Referência', 'Estoque positivo',
                        'Estoque negativo', 'Soma'],
            'fields': ['dep', 'ref', 'estoque',
                       'falta', 'soma'],
            'group': group,
            'data': data,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })

        return context

    def str_depositos(seft):
        texto = utils.functions.str.join(
            (', ', ' e '), (101, 102, 122, 231))
        return texto

    def get(self, request, *args, **kwargs):
        form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.Form_class(request.POST)
        if form.is_valid():
            deposito = form.cleaned_data['deposito']
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            self.context.update(self.mount_context(
                request, cursor, deposito, modelo))
        self.context['form'] = form
        return render(request, self.template_name, self.context)
