from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import utils.functions.strings
from utils.views import group_rowspan, totalize_grouped_data

import produto.queries

from estoque import forms, queries


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

        data = queries.referencia_deposito(cursor, modelo, deposito=deposito)
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
        texto = utils.functions.strings.join(
            (', ', ' e '), (101, 102, 103, 122, 231))
        return texto

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        form = self.Form_class(cursor=cursor)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        form = self.Form_class(request.POST, cursor=cursor)
        if form.is_valid():
            deposito = form.cleaned_data['deposito']
            modelo = form.cleaned_data['modelo']
            self.context.update(self.mount_context(
                request, cursor, deposito, modelo))
        self.context['form'] = form
        return render(request, self.template_name, self.context)
