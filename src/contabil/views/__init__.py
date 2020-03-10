from pprint import pprint
import urllib

from django.shortcuts import render
from django.urls import reverse
from django.db import connections
from django.views import View

from utils.views import totalize_grouped_data, totalize_data, group_rowspan

import contabil.forms as forms
import contabil.queries as queries

from .remeindu import *
from .remeindunf import *


def index(request):
    return render(request, 'contabil/index.html')


class InfAdProd(View):
    Form_class = forms.InfAdProdForm
    template_name = 'contabil/infadprod.html'
    title_name = 'Itens de pedido'

    def mount_context(self, pedido):
        context = {
            'pedido': pedido,
        }
        cursor = connections['so'].cursor()
        data = queries.infadprod_por_pedido(cursor, pedido)
        if len(data) == 0:
            context['erro'] = 'Pedido não encontrado'
        else:
            for row in data:
                row['VALOR_TOTAL'] = row['VALOR'] * row['QTD']
                if row['COUNT_GTIN'] == 0:
                    row['COUNT_GTIN'] = '-'
                elif row['COUNT_GTIN'] == 1:
                    row['COUNT_GTIN'] = 'Único'
                else:
                    row['COUNT_GTIN|LINK'] = '{}?{}'.format(
                        reverse('produto:gtin'),
                        urllib.parse.urlencode({
                            'gtin': row['GTIN'],
                        }))
                    row['COUNT_GTIN|TARGET'] = '_BLANK'

            totalize_grouped_data(data, {
                'group': [],
                'sum': ['QTD', 'VALOR_TOTAL'],
                'global_sum': ['QTD', 'VALOR_TOTAL'],
                'global_descr': {'REF': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })

            for row in data:
                row['VALOR|DECIMALS'] = 2
                row['VALOR_TOTAL|DECIMALS'] = 2
            row = data[0]
            context.update({
                'cliente': row['CLIENTE'],
                'headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Quantidade',
                            'Valor unitário', 'Valor total',
                            'Ref.Clie.(infAdProd)',
                            'Descr.Clie.(infAdProd)',
                            'GTIN', '#', 'Narrativa'),
                'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD',
                           'VALOR', 'VALOR_TOTAL',
                           'INFADPROD', 'DESCRCLI',
                           'GTIN', 'COUNT_GTIN', 'NARRATIVA'),
                'style': {
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    7: 'text-align: right;',
                },
                'data': data,
            })
        return context

    def get(self, request, *args, **kwargs):
        if 'pedido' in kwargs and kwargs['pedido'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'pedido' in kwargs and kwargs['pedido'] is not None:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            context.update(self.mount_context(pedido))
        context['form'] = form
        return render(request, self.template_name, context)


class NotaFiscal(View):
    Form_class = forms.NotaFiscalForm
    template_name = 'contabil/nota_fiscal.html'
    title_name = 'Nota fiscal'

    def mount_context(self, cursor, nf):
        context = {'nf': nf}

        # informações gerais
        data = queries.nf_inform(cursor, nf)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nota fiscal não encontrada',
            })
        else:
            for row in data:
                if row['SITUACAO'] == 1:
                    row['SITUACAO'] = 'Ativa'
                else:
                    row['SITUACAO'] = 'Cancelada'
                if row['NF_DEVOLUCAO'] is None:
                    row['NF_DEVOLUCAO'] = '-'
                else:
                    row['SITUACAO'] += '/Devolvida'
            context.update({
                'headers': ('Cliente', 'Data NFe', 'Situação', 'Valor',
                            'NF Devolução'),
                'fields': ('CLIENTE', 'DATA', 'SITUACAO', 'VALOR',
                           'NF_DEVOLUCAO'),
                'data': data,
            })

            # itens
            i_data = queries.nf_itens(cursor, nf)
            max_digits = 0
            for row in i_data:
                if row['PEDIDO_VENDA'] == 0:
                    row['PEDIDO_VENDA'] = '-'
                else:
                    row['PEDIDO_VENDA|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO_VENDA']])
                num_digits = str(row['QTDE_ITEM_FATUR'])[::-1].find('.')
                max_digits = max(max_digits, num_digits)
                row['VALOR_UNITARIO'] = \
                    row['VALOR_CONTABIL'] / row['QTDE_ITEM_FATUR']

            totalize_data(i_data, {
                'sum': ['QTDE_ITEM_FATUR', 'VALOR_CONTABIL'],
                'descr': {'NARRATIVA': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })

            for row in i_data:
                row['QTDE_ITEM_FATUR|DECIMALS'] = max_digits
                row['VALOR_UNITARIO|DECIMALS'] = 2
                row['VALOR_CONTABIL|DECIMALS'] = 2

            context.update({
                'i_headers': ['Seq.', 'Nível',
                              'Referência', 'Tamanho',
                              'Cor', 'Descrição', 'Quantidade',
                              'Valor unitário', 'Valor total',
                              'Pedido de venda'],
                'i_fields': ['SEQ_ITEM_NFISC', 'NIVEL_ESTRUTURA',
                             'GRUPO_ESTRUTURA', 'SUBGRU_ESTRUTURA',
                             'ITEM_ESTRUTURA', 'NARRATIVA', 'QTDE_ITEM_FATUR',
                             'VALOR_UNITARIO', 'VALOR_CONTABIL',
                             'PEDIDO_VENDA'],
                'i_data': i_data,
                'i_style': {
                    7: 'text-align: right;',
                    8: 'text-align: right;',
                    9: 'text-align: right;',
                    10: 'text-align: right;',
                },
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'nf' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'nf' in kwargs:
            form.data['nf'] = kwargs['nf']
        if form.is_valid():
            nf = form.cleaned_data['nf']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, nf))
        context['form'] = form
        return render(request, self.template_name, context)
