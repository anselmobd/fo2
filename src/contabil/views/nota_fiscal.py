from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

import contabil.forms as forms
import contabil.queries as queries


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
        form.data = form.data.copy()
        if 'nf' in kwargs:
            form.data['nf'] = kwargs['nf']
        if form.is_valid():
            nf = form.cleaned_data['nf']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, nf))
        context['form'] = form
        return render(request, self.template_name, context)
