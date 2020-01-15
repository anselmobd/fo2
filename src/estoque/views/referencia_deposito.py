from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.template import group_rowspan

from geral.functions import has_permission
from utils.views import totalize_grouped_data

import produto.queries

from estoque import forms
from estoque import queries


class ReferenciaDeposito(View):
    Form_class = forms.ReferenciasEstoqueForm
    template_name = 'estoque/referencia_deposito.html'
    title_name = 'Por referência de modelo em depósito'

    def mount_context(self, request, cursor, deposito, modelo):
        context = {
            'deposito': deposito,
            'modelo': modelo,
            'permission': has_permission(
                request, 'base.can_adjust_stock'),
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

        if has_permission(request, 'base.can_adjust_stock'):
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

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            deposito = form.cleaned_data['deposito']
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                request, cursor, deposito, modelo))
        context['form'] = form
        return render(request, self.template_name, context)
