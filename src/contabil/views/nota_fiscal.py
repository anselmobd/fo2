from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.views import totalize_data

import contabil.forms as forms
import contabil.queries as queries
from contabil.queries import nf_inform_
from contabil.functions.nf import nf_situacao_descr

class NotaFiscal(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotaFiscal, self).__init__(*args, **kwargs)
        self.Form_class = forms.NotaFiscalForm
        self.template_name = 'contabil/nota_fiscal.html'
        self.title_name = "Nota fiscal"
        self.get_args = ['nf', 'empresa']
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        self.context = {
            'titulo': self.title_name,
        }

        data = nf_inform_.nf_inform(
            cursor, self.nf, especiais=True, empresa=self.empresa)
        if len(data) == 0:
            self.context.update({
                'msg_erro': "Nota fiscal não encontrada",
            })
        else:
            for row in data:
                row['situacao'] = nf_situacao_descr(
                    row['situacao'], row['cod_status'])
                if row['nf_devolucao'] is None:
                    row['nf_devolucao'] = '-'
                else:
                    row['situacao'] = f"{row['situacao']}/Devolvida"
            self.context.update({
                'headers': [
                    "Cliente",
                    "Data NFe",
                    "Situação",
                    "Valor",
                    "NF Devolução",
                ],
                'fields': [
                    'cliente',
                    'data',
                    'situacao',
                    'valor',
                    'nf_devolucao',
                ],
                'data': data,
            })

            i_data = queries.nf_itens(cursor, self.nf, especiais=True, empresa=self.empresa)
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
                'descr': {'NARRATIVA': "Totais:"},
                'row_style': 'font-weight: bold;',
            })

            for row in i_data:
                row['QTDE_ITEM_FATUR|DECIMALS'] = max_digits
                row['VALOR_UNITARIO|DECIMALS'] = 2
                row['VALOR_CONTABIL|DECIMALS'] = 2

            self.context.update({
                'i_headers': [
                    "Seq.",
                    "Nível",
                    "Referência",
                    "Tamanho",
                    "Cor",
                    "Descrição",
                    "Quantidade",
                    "Valor unitário",
                    "Valor total",
                    "Pedido de venda",
                ],
                'i_fields': [
                    'SEQ_ITEM_NFISC',
                    'NIVEL_ESTRUTURA',
                    'GRUPO_ESTRUTURA',
                    'SUBGRU_ESTRUTURA',
                    'ITEM_ESTRUTURA',
                    'NARRATIVA',
                    'QTDE_ITEM_FATUR',
                    'VALOR_UNITARIO',
                    'VALOR_CONTABIL',
                    'PEDIDO_VENDA',
                ],
                'i_data': i_data,
                'i_style': {
                    7: 'text-align: right;',
                    8: 'text-align: right;',
                    9: 'text-align: right;',
                    10: 'text-align: right;',
                },
            })
