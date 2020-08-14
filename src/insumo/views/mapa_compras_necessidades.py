import re
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

import insumo.queries as queries
from insumo.forms import MapaComprasNecessidadesForm


class MapaComprasNecessidades(View):
    Form_class = MapaComprasNecessidadesForm
    template_name = 'insumo/necessidade.html'
    title_name = 'Necessidade (mapa)'

    def mount_context(
            self, cursor, op, data_corte, data_corte_ate, periodo_corte,
            data_compra, data_compra_ate, periodo_compra,
            insumo, conta_estoque,
            ref, conta_estoque_ref, colecao, quais):
        context = {}
        if not (op or data_corte or data_corte_ate or periodo_corte or
                data_compra or data_compra_ate or periodo_compra or
                insumo or conta_estoque or
                ref or conta_estoque_ref or colecao):
            context.update({
                'msg_erro': 'Especifique ao menos um filtro',
            })
            return context
        context.update({
            'op': op,
            'data_corte': data_corte,
            'data_corte_ate': data_corte_ate,
            'periodo_corte': periodo_corte,
            'data_compra': data_compra,
            'data_compra_ate': data_compra_ate,
            'periodo_compra': periodo_compra,
            'insumo': insumo,
            'conta_estoque': conta_estoque,
            'ref': ref,
            'conta_estoque_ref': conta_estoque_ref,
            'colecao': colecao,
            'quais': quais,
        })

        data = queries.necessidade(
            cursor, op, data_corte, data_corte_ate, periodo_corte,
            data_compra, data_compra_ate, periodo_compra,
            insumo, conta_estoque,
            ref, conta_estoque_ref, colecao, quais)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma necessidade de insumos encontrada',
            })
            return context

        for row in data:
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            row['OPS'] = re.sub(
                r'([1234567890]+)',
                r'<a href="/lotes/op/\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>',
                str(row['OPS']))
            row['REFS'] = re.sub(
                r'([^, ]+)',
                r'<a href="{produto_ref}\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>'.format(
                    produto_ref=reverse('produto:ref')),
                str(row['REFS']))
        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição',
                        'Cor', 'Tamanho',
                        'Necessidade', 'Unid.',
                        'Produzido', 'OPs',
                        'Estoq. Mínimo', 'Reposição'),
            'fields': ('NIVEL', 'REF', 'DESCR',
                       'COR', 'TAM',
                       'QTD', 'UNID',
                       'REFS', 'OPS',
                       'STQ_MIN', 'REPOSICAO'),
            'safe': ('REFS', 'OPS'),
            'data': data,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            data_corte = form.cleaned_data['data_corte']
            data_corte_ate = form.cleaned_data['data_corte_ate']
            periodo_corte = form.cleaned_data['periodo_corte']
            data_compra = form.cleaned_data['data_compra']
            data_compra_ate = form.cleaned_data['data_compra_ate']
            periodo_compra = form.cleaned_data['periodo_compra']
            insumo = form.cleaned_data['insumo']
            conta_estoque = form.cleaned_data['conta_estoque']
            ref = form.cleaned_data['ref']
            conta_estoque_ref = form.cleaned_data['conta_estoque_ref']
            colecao = form.cleaned_data['colecao']
            quais = form.cleaned_data['quais']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, op, data_corte, data_corte_ate, periodo_corte,
                data_compra, data_compra_ate, periodo_compra,
                insumo, conta_estoque,
                ref, conta_estoque_ref, colecao, quais))
        context['form'] = form
        return render(request, self.template_name, context)
