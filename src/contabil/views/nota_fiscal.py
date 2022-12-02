from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views.o2.get_post import O2BaseGetPostView
from utils.views import totalize_data

import contabil.forms.nf
from contabil.queries import (
    nf_inform,
    nf_itens,
)
from contabil.functions.nf import nf_situacao_descr


class NotaFiscal(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotaFiscal, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.nf.NotaFiscalForm
        self.template_name = 'contabil/nota_fiscal.html'
        self.title_name = "Nota fiscal"
        self.get_args = ['nf', 'empresa']
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        self.context = {
            'titulo': self.title_name,
        }

        data = nf_inform.query(
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

            i_data = nf_itens.query(cursor, self.nf, especiais=True, empresa=self.empresa)
            max_digits = 0
            for row in i_data:
                if row['pedido_venda'] == 0:
                    row['pedido_venda'] = '-'
                else:
                    row['pedido_venda|LINK'] = reverse(
                        'producao:pedido__get', args=[row['pedido_venda']])
                num_digits = str(row['qtde_item_fatur'])[::-1].find('.')
                max_digits = max(max_digits, num_digits)
                row['valor_unitario'] = \
                    row['valor_contabil'] / row['qtde_item_fatur']

            totalize_data(i_data, {
                'sum': ['qtde_item_fatur', 'valor_contabil'],
                'descr': {'narrativa': "Totais:"},
                'row_style': 'font-weight: bold;',
            })

            for row in i_data:
                row['qtde_item_fatur|DECIMALS'] = max_digits
                row['valor_unitario|DECIMALS'] = 2
                row['valor_contabil|DECIMALS'] = 2

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
                    'seq_item_nfisc',
                    'nivel_estrutura',
                    'grupo_estrutura',
                    'subgru_estrutura',
                    'item_estrutura',
                    'narrativa',
                    'qtde_item_fatur',
                    'valor_unitario',
                    'valor_contabil',
                    'pedido_venda',
                ],
                'i_data': i_data,
                'i_style': {
                    7: 'text-align: right;',
                    8: 'text-align: right;',
                    9: 'text-align: right;',
                    10: 'text-align: right;',
                },
            })
