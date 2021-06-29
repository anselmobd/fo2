from pprint import pprint
import urllib

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data

import contabil.forms as forms
import contabil.queries as queries


class InfAdProd(View):
    Form_class = forms.InfAdProdForm
    template_name = 'contabil/infadprod.html'
    title_name = 'Itens de pedido'

    def mount_context(self, pedido):
        context = {
            'pedido': pedido,
        }
        cursor = db_cursor_so(self.request)
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
                        reverse('produto:gtin_pesquisa'),
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
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
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
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'pedido' in kwargs and kwargs['pedido'] is not None:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            context.update(self.mount_context(pedido))
        context['form'] = form
        return render(request, self.template_name, context)
