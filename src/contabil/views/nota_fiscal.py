from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
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
            return

        tem_ped = False
        for row in data:
            if row['ped']:
                tem_ped = True
                row['ped|TARGET'] = '_blank'
                row['ped|A'] = reverse(
                    'producao:pedido__get',
                    args=[row['ped']],
                )
            if row['ped_obs'] is None:
                row['ped_obs'] = '-'
            row['situacao'] = nf_situacao_descr(
                row['situacao'], row['cod_status'])
            if row['nf_devolucao']:
                row['situacao'] = f"{row['situacao']}/Devolvida"
                row['nf_devolucao|TARGET'] = '_blank'
                row['nf_devolucao|A'] = reverse(
                    'contabil:nf_recebida__get2',
                    args=[
                        self.empresa,
                        row['nf_devolucao'],
                    ],
                )
            else:
                row['nf_devolucao'] = '-'
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

        if tem_ped:
            self.context.update({
                'pedido': {
                    'headers': ('Pedido', 'Observação'),
                    'fields': ('ped', 'ped_obs'),
                    'data': data,
                    'titulo': "Pedido da NF",
                },
            })


        i_data = nf_itens.query(cursor, self.nf, especiais=True, empresa=self.empresa)
        max_digits = 0
        for row in i_data:
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
            ],
            'i_data': i_data,
            'i_style': {
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
        })
